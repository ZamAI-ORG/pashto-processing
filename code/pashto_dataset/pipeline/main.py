"""
Main pipeline runner for the Pashto dataset creation process.
"""

import os
import sys
import time
import signal
import threading
from typing import Dict, List, Optional, Any, Callable
from datetime import datetime
from pathlib import Path
from dataclasses import dataclass
from enum import Enum
import argparse
import json

# Import pipeline components
try:
    # Try relative imports first (when used as package)
    from .config import ConfigManager, PipelineConfig, PipelineStepConfig
    from .logging_monitoring import PipelineLogger, MetricsCollector, MonitoringDashboard
    from .progress_error_recovery import ProgressTracker, ErrorRecovery, progress_context
    from .validation import ValidationEngine, ValidationLevel, ValidationReport
    from .scheduler import PipelineScheduler, ScheduleConfig, ScheduleType, ScheduleStatus
except ImportError:
    # Fall back to absolute imports (for standalone testing)
    from config import ConfigManager, PipelineConfig, PipelineStepConfig
    from logging_monitoring import PipelineLogger, MetricsCollector, MonitoringDashboard
    from progress_error_recovery import ProgressTracker, ErrorRecovery, progress_context
    from validation import ValidationEngine, ValidationLevel, ValidationReport
    from scheduler import PipelineScheduler, ScheduleConfig, ScheduleType, ScheduleStatus


class PipelineState(Enum):
    """Pipeline execution state."""
    IDLE = "idle"
    INITIALIZING = "initializing"
    RUNNING = "running"
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class PipelineExecutionContext:
    """Pipeline execution context."""
    pipeline_id: str
    start_time: datetime
    configuration: PipelineConfig
    state: PipelineState
    current_step: Optional[str] = None
    completed_steps: List[str] = None
    failed_steps: List[str] = None
    cancelled_steps: List[str] = None
    error_count: int = 0
    warning_count: int = 0
    retry_count: int = 0
    
    def __post_init__(self):
        if self.completed_steps is None:
            self.completed_steps = []
        if self.failed_steps is None:
            self.failed_steps = []
        if self.cancelled_steps is None:
            self.cancelled_steps = []


class PipelineRunner:
    """Main pipeline runner orchestrating all components."""
    
    def __init__(self, config_path: str = None):
        # Initialize components
        self.config_manager = ConfigManager()
        self.pipeline_config = self.config_manager.load_pipeline_config()
        self.step_configs = self.config_manager.load_step_configs()
        
        # Update config if custom config path provided
        if config_path:
            self._load_custom_config(config_path)
        
        # Create pipeline ID
        self.pipeline_id = f"pashto_pipeline_{int(time.time())}"
        
        # Initialize components with pipeline config
        self.logger = PipelineLogger(
            name="pashto_pipeline",
            logs_path=os.path.join(self.pipeline_config.base_path, self.pipeline_config.logs_path),
            log_level=self.pipeline_config.log_level,
            log_format=self.pipeline_config.log_format,
            log_rotation=self.pipeline_config.log_rotation,
            log_retention_days=self.pipeline_config.log_retention_days
        )
        
        self.metrics_collector = MetricsCollector(
            pipeline_id=self.pipeline_id,
            logs_path=os.path.join(self.pipeline_config.base_path, self.pipeline_config.logs_path)
        )
        
        self.progress_tracker = ProgressTracker(
            pipeline_id=self.pipeline_id,
            logs_path=os.path.join(self.pipeline_config.base_path, self.pipeline_config.logs_path)
        )
        
        self.error_recovery = ErrorRecovery(
            logs_path=os.path.join(self.pipeline_config.base_path, self.pipeline_config.logs_path)
        )
        
        self.validation_engine = ValidationEngine(
            logs_path=os.path.join(self.pipeline_config.base_path, self.pipeline_config.logs_path)
        )
        
        self.scheduler = PipelineScheduler(self.pipeline_config.base_path)
        
        # Create monitoring dashboard
        self.monitoring_dashboard = MonitoringDashboard(
            metrics_collector=self.metrics_collector,
            logger=self.logger
        )
        
        # Pipeline execution state
        self.execution_context = PipelineExecutionContext(
            pipeline_id=self.pipeline_id,
            start_time=datetime.now(),
            configuration=self.pipeline_config,
            state=PipelineState.IDLE
        )
        
        # Register default pipeline steps
        self._register_default_steps()
        
        # Signal handlers
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
        
        # Progress tracking callbacks
        self.progress_tracker.register_callback(self._on_progress_update)
        
        self.logger.info(f"Pipeline runner initialized with ID: {self.pipeline_id}")
    
    def _load_custom_config(self, config_path: str):
        """Load custom configuration file."""
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                custom_config = json.load(f)
            
            # Update pipeline config
            for key, value in custom_config.items():
                if hasattr(self.pipeline_config, key):
                    setattr(self.pipeline_config, key, value)
            
            self.logger.info(f"Loaded custom configuration from: {config_path}")
        except Exception as e:
            self.logger.error(f"Failed to load custom config: {str(e)}")
    
    def _register_default_steps(self):
        """Register default pipeline steps and their implementations."""
        self.step_implementations = {
            "data_collection": self._step_data_collection,
            "data_cleaning": self._step_data_cleaning,
            "text_normalization": self._step_text_normalization,
            "data_validation": self._step_data_validation,
            "format_conversion": self._step_format_conversion,
            "quality_check": self._step_quality_check
        }
        
        # Register validation rules for each step
        self._register_step_validations()
    
    def _register_step_validations(self):
        """Register validation rules for each pipeline step."""
        # Data collection validations
        self.validation_engine.register_step_validator("data_collection", [
            self.validation_engine.rules[0]  # file_exists
        ])
        
        # Data cleaning validations
        self.validation_engine.register_step_validator("data_cleaning", [
            self.validation_engine.rules[0],  # file_exists
            self.validation_engine.rules[1],  # file_format
            self.validation_engine.rules[2],  # data_quality
        ])
        
        # Text normalization validations
        self.validation_engine.register_step_validator("text_normalization", [
            self.validation_engine.rules[1],  # file_format
            self.validation_engine.rules[2],  # data_quality
            self.validation_engine.rules[3],  # language_detection
        ])
        
        # Data validation validations
        self.validation_engine.register_step_validator("data_validation", [
            self.validation_engine.rules[1],  # file_format
            self.validation_engine.rules[4],  # encoding
            self.validation_engine.rules[5],  # completeness
        ])
        
        # Format conversion validations
        self.validation_engine.register_step_validator("format_conversion", [
            self.validation_engine.rules[0],  # file_exists
            self.validation_engine.rules[1],  # file_format
            self.validation_engine.rules[2],  # data_quality
        ])
        
        # Quality check validations
        self.validation_engine.register_step_validator("quality_check", [
            self.validation_engine.rules[5],  # completeness
            self.validation_engine.rules[6],  # consistency
            self.validation_engine.rules[7],  # metadata
        ])
    
    def run_full_pipeline(self, steps: List[str] = None) -> bool:
        """Run the complete pipeline or specified steps."""
        self.logger.info("Starting pipeline execution")
        self.execution_context.state = PipelineState.INITIALIZING
        
        try:
            # Set up steps
            if steps is None:
                steps = [name for name, config in self.step_configs.items() if config.enabled]
            
            # Validate steps exist
            missing_steps = [step for step in steps if step not in self.step_implementations]
            if missing_steps:
                self.logger.error(f"Missing step implementations: {missing_steps}")
                return False
            
            # Set up progress tracking
            self.progress_tracker.set_steps(steps, total_records=10000)  # Estimated total
            
            self.execution_context.state = PipelineState.RUNNING
            
            # Execute steps in dependency order
            execution_order = self._get_execution_order(steps)
            
            with self.metrics_collector.start_step("pipeline_execution") as pipeline_step:
                for step_name in execution_order:
                    if not self._execute_step(step_name):
                        self.execution_context.state = PipelineState.FAILED
                        return False
                
                self.execution_context.state = PipelineState.COMPLETED
                return True
        
        except KeyboardInterrupt:
            self.logger.info("Pipeline interrupted by user")
            self.execution_context.state = PipelineState.CANCELLED
            self._cleanup_on_cancel()
            return False
        
        except Exception as e:
            self.logger.error(f"Pipeline execution failed: {str(e)}")
            self.execution_context.state = PipelineState.FAILED
            return False
        
        finally:
            # Complete pipeline metrics
            self.metrics_collector.complete_step(
                "pipeline_execution",
                status="completed" if self.execution_context.state == PipelineState.COMPLETED else "failed"
            )
    
    def _execute_step(self, step_name: str) -> bool:
        """Execute a single pipeline step."""
        step_config = self.step_configs.get(step_name)
        if not step_config:
            self.logger.error(f"Step configuration not found: {step_name}")
            return False
        
        if not step_config.enabled:
            self.logger.info(f"Skipping disabled step: {step_name}")
            self.progress_tracker.skip_step(step_name)
            return True
        
        self.logger.info(f"Starting step: {step_name}")
        self.execution_context.current_step = step_name
        
        # Check retry conditions
        if not self._can_retry_step(step_name, step_config):
            self.logger.error(f"Step {step_name} cannot be retried further")
            return False
        
        try:
            # Start metrics collection
            step_metrics = self.metrics_collector.start_step(
                step_name,
                input_files=self._get_step_input_files(step_name)
            )
            
            # Execute step with progress tracking
            with progress_context(self.progress_tracker, step_name, 
                                total_records=1000, logger=self.logger) as tracker:
                success = self._run_step_implementation(step_name, step_config, tracker)
            
            # Complete step
            self.metrics_collector.complete_step(
                step_name,
                status="completed" if success else "failed",
                output_files=self._get_step_output_files(step_name),
                records_processed=tracker.step_records.get(step_name, 0)
            )
            
            if success:
                self.execution_context.completed_steps.append(step_name)
                self.logger.info(f"Step completed successfully: {step_name}")
                
                # Run validation if required
                if step_config.validation_required and self.pipeline_config.auto_validation:
                    self._validate_step(step_name)
                
                # Clear errors for successful step
                self.error_recovery.clear_errors_for_step(step_name)
                
                return True
            else:
                self.execution_context.failed_steps.append(step_name)
                self.execution_context.error_count += 1
                self._handle_step_failure(step_name)
                return False
        
        except Exception as e:
            self.execution_context.error_count += 1
            self._handle_step_exception(step_name, e)
            return False
    
    def _run_step_implementation(self, step_name: str, step_config: PipelineStepConfig, 
                               tracker: ProgressTracker) -> bool:
        """Run the actual step implementation."""
        implementation = self.step_implementations.get(step_name)
        if not implementation:
            self.logger.error(f"Step implementation not found: {step_name}")
            return False
        
        try:
            # Set timeout if specified
            if step_config.timeout:
                # In a real implementation, you would use signal.alarm or threading timeout
                pass
            
            # Call step implementation
            return implementation(step_config.custom_config or {}, tracker)
        
        except Exception as e:
            self.logger.error(f"Step implementation error: {step_name} - {str(e)}")
            return False
    
    def _step_data_collection(self, config: Dict[str, Any], tracker: ProgressTracker) -> bool:
        """Data collection step implementation."""
        self.logger.info("Collecting data...")
        
        # Simulate data collection
        for i in range(100):
            time.sleep(0.01)  # Simulate work
            tracker.update_step_progress("data_collection", i + 1)
        
        return True
    
    def _step_data_cleaning(self, config: Dict[str, Any], tracker: ProgressTracker) -> bool:
        """Data cleaning step implementation."""
        self.logger.info("Cleaning data...")
        
        # Simulate data cleaning
        for i in range(50):
            time.sleep(0.02)  # Simulate work
            tracker.update_step_progress("data_cleaning", i + 1)
        
        return True
    
    def _step_text_normalization(self, config: Dict[str, Any], tracker: ProgressTracker) -> bool:
        """Text normalization step implementation."""
        self.logger.info("Normalizing text...")
        
        # Simulate text normalization
        for i in range(80):
            time.sleep(0.01)  # Simulate work
            tracker.update_step_progress("text_normalization", i + 1)
        
        return True
    
    def _step_data_validation(self, config: Dict[str, Any], tracker: ProgressTracker) -> bool:
        """Data validation step implementation."""
        self.logger.info("Validating data...")
        
        # Simulate data validation
        for i in range(30):
            time.sleep(0.02)  # Simulate work
            tracker.update_step_progress("data_validation", i + 1)
        
        return True
    
    def _step_format_conversion(self, config: Dict[str, Any], tracker: ProgressTracker) -> bool:
        """Format conversion step implementation."""
        self.logger.info("Converting format...")
        
        # Simulate format conversion
        for i in range(40):
            time.sleep(0.015)  # Simulate work
            tracker.update_step_progress("format_conversion", i + 1)
        
        return True
    
    def _step_quality_check(self, config: Dict[str, Any], tracker: ProgressTracker) -> bool:
        """Quality check step implementation."""
        self.logger.info("Performing quality check...")
        
        # Simulate quality check
        for i in range(20):
            time.sleep(0.01)  # Simulate work
            tracker.update_step_progress("quality_check", i + 1)
        
        return True
    
    def _validate_step(self, step_name: str) -> bool:
        """Validate a step's output."""
        try:
            data_path = self._get_step_output_path(step_name)
            validation_level = ValidationLevel(self.pipeline_config.validation_level)
            
            report = self.validation_engine.validate_step(
                step_name=step_name,
                data_path=data_path,
                validation_level=validation_level
            )
            
            if report.overall_status.value == "failed":
                self.logger.warning(f"Step validation failed: {step_name}")
                return False
            else:
                self.logger.info(f"Step validation passed: {step_name}")
                return True
        
        except Exception as e:
            self.logger.error(f"Step validation error: {step_name} - {str(e)}")
            return False
    
    def _get_execution_order(self, steps: List[str]) -> List[str]:
        """Get execution order based on dependencies."""
        # Simple dependency resolution
        order = []
        remaining = set(steps)
        visited = set()
        
        def visit(step):
            if step in visited:
                return
            visited.add(step)
            
            # Visit dependencies first
            step_config = self.step_configs.get(step)
            if step_config:
                for dep in step_config.dependencies:
                    if dep in remaining:
                        visit(dep)
            
            if step in remaining:
                order.append(step)
                remaining.remove(step)
        
        for step in steps:
            if step in remaining:
                visit(step)
        
        return order
    
    def _can_retry_step(self, step_name: str, step_config: PipelineStepConfig) -> bool:
        """Check if a step can be retried."""
        if step_config.retry_count >= self.pipeline_config.max_retries:
            return False
        
        if not self.error_recovery.can_retry(
            step_name,
            self.pipeline_config.max_retries,
            self.pipeline_config.retry_delay,
            self.pipeline_config.exponential_backoff
        ):
            return False
        
        return True
    
    def _get_step_input_files(self, step_name: str) -> List[str]:
        """Get input files for a step."""
        # This would be implemented based on your specific file structure
        return []
    
    def _get_step_output_files(self, step_name: str) -> List[str]:
        """Get output files for a step."""
        # This would be implemented based on your specific file structure
        return []
    
    def _get_step_output_path(self, step_name: str) -> str:
        """Get output path for a step."""
        base_path = self.pipeline_config.base_path
        output_path = os.path.join(base_path, self.pipeline_config.output_path)
        return output_path
    
    def _handle_step_failure(self, step_name: str):
        """Handle step failure."""
        self.error_recovery.increment_retry_count(step_name)
        
        recovery_suggestions = self.error_recovery.get_recovery_suggestions(step_name)
        if recovery_suggestions:
            self.logger.warning(f"Recovery suggestions for {step_name}: {recovery_suggestions}")
    
    def _handle_step_exception(self, step_name: str, exception: Exception):
        """Handle step exception."""
        error_info = self.error_recovery.add_error(
            step_name=step_name,
            error=exception,
            is_recoverable=True
        )
        
        self.logger.error(f"Step exception in {step_name}: {str(exception)}")
    
    def _on_progress_update(self, progress_info):
        """Handle progress updates."""
        if progress_info.overall_progress > 0:
            self.monitoring_dashboard.update(force=True)
        
        if progress_info.overall_progress % 10 == 0:  # Log every 10%
            self.logger.info(f"Progress: {progress_info.overall_progress:.1f}% - "
                           f"Step: {progress_info.current_step} "
                           f"({progress_info.completed_steps}/{progress_info.total_steps})")
    
    def _signal_handler(self, signum, frame):
        """Handle system signals."""
        self.logger.info(f"Received signal {signum}, shutting down gracefully...")
        self.execution_context.state = PipelineState.CANCELLED
        self._cleanup_on_cancel()
        sys.exit(0)
    
    def _cleanup_on_cancel(self):
        """Cleanup when pipeline is cancelled."""
        try:
            # Cancel progress tracking
            self.progress_tracker.cancel_pipeline()
            
            # Update metrics
            self.metrics_collector.complete_pipeline("cancelled")
            
            self.logger.info("Pipeline cleanup completed")
        
        except Exception as e:
            self.logger.error(f"Cleanup error: {str(e)}")
    
    def get_status(self) -> Dict[str, Any]:
        """Get current pipeline status."""
        progress_info = self.progress_tracker.get_progress_info()
        metrics = self.metrics_collector.get_metrics()
        status_summary = self.monitoring_dashboard.get_status_summary()
        
        return {
            "pipeline_id": self.pipeline_id,
            "state": self.execution_context.state.value,
            "execution_context": {
                "current_step": self.execution_context.current_step,
                "completed_steps": self.execution_context.completed_steps,
                "failed_steps": self.execution_context.failed_steps,
                "error_count": self.execution_context.error_count,
                "warning_count": self.execution_context.warning_count
            },
            "progress": status_summary,
            "metrics": {
                "start_time": metrics.start_time.isoformat(),
                "total_duration": metrics.total_duration,
                "peak_memory_mb": metrics.peak_memory_mb,
                "peak_cpu_percent": metrics.peak_cpu_percent
            }
        }
    
    def stop(self):
        """Stop the pipeline."""
        self.logger.info("Stopping pipeline...")
        self.execution_context.state = PipelineState.CANCELLED
        self._cleanup_on_cancel()


def main():
    """Main entry point for the pipeline."""
    parser = argparse.ArgumentParser(description="Pashto Dataset Pipeline Runner")
    parser.add_argument("--config", type=str, help="Custom configuration file path")
    parser.add_argument("--steps", type=str, nargs="+", help="Specific steps to run")
    parser.add_argument("--status", action="store_true", help="Show pipeline status")
    parser.add_argument("--test", action="store_true", help="Run pipeline tests")
    
    args = parser.parse_args()
    
    try:
        # Initialize pipeline runner
        runner = PipelineRunner(config_path=args.config)
        
        if args.status:
            # Show status
            status = runner.get_status()
            print(json.dumps(status, indent=2, default=str))
        
        elif args.test:
            # Run tests
            from .testing import PipelineTester
            tester = PipelineTester(runner)
            results = tester.run_all_tests()
            print(f"Test results: {results}")
        
        else:
            # Run pipeline
            steps = args.steps if args.steps else None
            success = runner.run_full_pipeline(steps=steps)
            sys.exit(0 if success else 1)
    
    except Exception as e:
        print(f"Pipeline runner error: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()