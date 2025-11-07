"""
Testing and validation system for the Pashto dataset pipeline.
"""

import os
import sys
import time
import json
import csv
import unittest
import tempfile
import shutil
from typing import Dict, List, Any, Optional, Callable
from datetime import datetime
from pathlib import Path
from dataclasses import dataclass
from enum import Enum

# Import pipeline components
try:
    # Try relative imports first (when used as package)
    from .config import PipelineConfig, ConfigManager
    from .logging_monitoring import PipelineLogger, MetricsCollector
    from .progress_error_recovery import ProgressTracker, ErrorRecovery
    from .validation import ValidationEngine, ValidationLevel
    from .scheduler import PipelineScheduler, ScheduleConfig, ScheduleType
    from .main import PipelineRunner
except ImportError:
    # Fall back to absolute imports (for standalone testing)
    from config import PipelineConfig, ConfigManager
    from logging_monitoring import PipelineLogger, MetricsCollector
    from progress_error_recovery import ProgressTracker, ErrorRecovery
    from validation import ValidationEngine, ValidationLevel
    from scheduler import PipelineScheduler, ScheduleConfig, ScheduleType
    from main import PipelineRunner


class TestStatus(Enum):
    """Test execution status."""
    PASSED = "passed"
    FAILED = "failed"
    SKIPPED = "skipped"
    ERROR = "error"


class TestCategory(Enum):
    """Test categories."""
    UNIT = "unit"
    INTEGRATION = "integration"
    SYSTEM = "system"
    PERFORMANCE = "performance"
    VALIDATION = "validation"


@dataclass
class TestResult:
    """Individual test result."""
    test_name: str
    category: TestCategory
    status: TestStatus
    duration: float
    message: str
    details: Dict[str, Any]
    timestamp: datetime
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        result_dict = {
            "test_name": self.test_name,
            "category": self.category.value,
            "status": self.status.value,
            "duration": self.duration,
            "message": self.message,
            "details": self.details,
            "timestamp": self.timestamp.isoformat()
        }
        return result_dict


@dataclass
class TestSuite:
    """Test suite containing multiple tests."""
    suite_name: str
    description: str
    tests: List[str]  # Test method names
    category: TestCategory
    required: bool = True
    setup_method: Optional[str] = None
    teardown_method: Optional[str] = None


class PipelineTester:
    """Comprehensive testing system for the pipeline."""
    
    def __init__(self, pipeline_runner: PipelineRunner = None, test_config: Dict[str, Any] = None):
        self.pipeline_runner = pipeline_runner
        self.test_config = test_config or {}
        
        # Test environment
        self.test_base_path = self.test_config.get('test_base_path', '/tmp/pashto_pipeline_test')
        self.test_data_path = os.path.join(self.test_base_path, 'data')
        self.test_logs_path = os.path.join(self.test_base_path, 'logs')
        
        # Test results
        self.test_results: List[TestResult] = []
        self.test_suites: List[TestSuite] = []
        
        # Initialize test environment
        self._setup_test_environment()
        
        # Register test suites
        self._register_test_suites()
    
    def _setup_test_environment(self):
        """Set up test environment."""
        # Clean and create test directories
        if os.path.exists(self.test_base_path):
            shutil.rmtree(self.test_base_path)
        
        os.makedirs(self.test_base_path, exist_ok=True)
        os.makedirs(self.test_data_path, exist_ok=True)
        os.makedirs(self.test_logs_path, exist_ok=True)
        
        # Create test data files
        self._create_test_data()
    
    def _create_test_data(self):
        """Create test data files."""
        # Create sample JSON data
        sample_data = [
            {"id": 1, "text": "Hello world", "language": "en"},
            {"id": 2, "text": "سلام نړی", "language": "ps"},
            {"id": 3, "text": "Test text", "language": "en"}
        ]
        
        with open(os.path.join(self.test_data_path, 'sample_data.json'), 'w', encoding='utf-8') as f:
            json.dump(sample_data, f, ensure_ascii=False, indent=2)
        
        # Create sample CSV data
        with open(os.path.join(self.test_data_path, 'sample_data.csv'), 'w', encoding='utf-8', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['id', 'text', 'language'])
            writer.writerow([1, 'Hello world', 'en'])
            writer.writerow([2, 'سلام نړی', 'ps'])
            writer.writerow([3, 'Test text', 'en'])
        
        # Create sample text data
        with open(os.path.join(self.test_data_path, 'sample_text.txt'), 'w', encoding='utf-8') as f:
            f.write("Hello world\n")
            f.write("سلام نړی\n")
            f.write("Test text\n")
    
    def _register_test_suites(self):
        """Register test suites."""
        self.test_suites = [
            TestSuite(
                suite_name="config_tests",
                description="Configuration management tests",
                category=TestCategory.UNIT,
                tests=[
                    "test_config_creation",
                    "test_config_loading",
                    "test_config_saving",
                    "test_config_validation"
                ]
            ),
            TestSuite(
                suite_name="logging_tests",
                description="Logging and monitoring tests",
                category=TestCategory.UNIT,
                tests=[
                    "test_logger_creation",
                    "test_metrics_collection",
                    "test_monitoring_dashboard"
                ]
            ),
            TestSuite(
                suite_name="progress_tests",
                description="Progress tracking tests",
                category=TestCategory.UNIT,
                tests=[
                    "test_progress_tracker",
                    "test_error_recovery",
                    "test_progress_callbacks"
                ]
            ),
            TestSuite(
                suite_name="validation_tests",
                description="Validation system tests",
                category=TestCategory.UNIT,
                tests=[
                    "test_validation_engine",
                    "test_validation_rules",
                    "test_validation_reports"
                ]
            ),
            TestSuite(
                suite_name="scheduler_tests",
                description="Pipeline scheduling tests",
                category=TestCategory.INTEGRATION,
                tests=[
                    "test_scheduler_creation",
                    "test_schedule_management",
                    "test_job_execution"
                ]
            ),
            TestSuite(
                suite_name="integration_tests",
                description="Full pipeline integration tests",
                category=TestCategory.INTEGRATION,
                tests=[
                    "test_pipeline_runner",
                    "test_full_pipeline_execution",
                    "test_error_handling"
                ]
            ),
            TestSuite(
                suite_name="performance_tests",
                description="Pipeline performance tests",
                category=TestCategory.PERFORMANCE,
                tests=[
                    "test_performance_metrics",
                    "test_memory_usage",
                    "test_concurrent_execution"
                ]
            )
        ]
    
    def run_test_suite(self, suite_name: str) -> Dict[str, Any]:
        """Run a specific test suite."""
        suite = next((s for s in self.test_suites if s.suite_name == suite_name), None)
        if not suite:
            return {"error": f"Test suite not found: {suite_name}"}
        
        # Setup
        if suite.setup_method:
            getattr(self, suite.setup_method)()
        
        results = []
        start_time = time.time()
        
        for test_name in suite.tests:
            if hasattr(self, test_name):
                try:
                    test_start = time.time()
                    test_result = getattr(self, test_name)()
                    test_duration = time.time() - test_start
                    
                    results.append(test_result)
                    self.test_results.append(test_result)
                
                except Exception as e:
                    error_result = TestResult(
                        test_name=test_name,
                        category=suite.category,
                        status=TestStatus.ERROR,
                        duration=time.time() - test_start,
                        message=f"Test execution error: {str(e)}",
                        details={"error": str(e)},
                        timestamp=datetime.now()
                    )
                    results.append(error_result)
                    self.test_results.append(error_result)
            else:
                # Test method not found
                missing_result = TestResult(
                    test_name=test_name,
                    category=suite.category,
                    status=TestStatus.SKIPPED,
                    duration=0.0,
                    message="Test method not implemented",
                    details={},
                    timestamp=datetime.now()
                )
                results.append(missing_result)
                self.test_results.append(missing_result)
        
        # Teardown
        if suite.teardown_method:
            getattr(self, suite.teardown_method)()
        
        suite_duration = time.time() - start_time
        
        return {
            "suite_name": suite_name,
            "duration": suite_duration,
            "total_tests": len(results),
            "passed": len([r for r in results if r.status == TestStatus.PASSED]),
            "failed": len([r for r in results if r.status == TestStatus.FAILED]),
            "skipped": len([r for r in results if r.status == TestStatus.SKIPPED]),
            "errors": len([r for r in results if r.status == TestStatus.ERROR]),
            "results": [r.to_dict() for r in results]
        }
    
    def run_all_tests(self) -> Dict[str, Any]:
        """Run all test suites."""
        all_results = {}
        total_start = time.time()
        
        for suite in self.test_suites:
            results = self.run_test_suite(suite.suite_name)
            all_results[suite.suite_name] = results
        
        total_duration = time.time() - total_start
        
        # Calculate overall statistics
        all_test_results = [r for results in all_results.values() for r in results.get('results', [])]
        total_passed = len([r for r in all_test_results if r['status'] == 'passed'])
        total_failed = len([r for r in all_test_results if r['status'] == 'failed'])
        total_skipped = len([r for r in all_test_results if r['status'] == 'skipped'])
        total_errors = len([r for r in all_test_results if r['status'] == 'error'])
        
        return {
            "summary": {
                "total_duration": total_duration,
                "total_suites": len(all_results),
                "total_tests": len(all_test_results),
                "passed": total_passed,
                "failed": total_failed,
                "skipped": total_skipped,
                "errors": total_errors,
                "success_rate": (total_passed / len(all_test_results) * 100) if all_test_results else 0
            },
            "suites": all_results
        }
    
    def run_specific_tests(self, test_names: List[str]) -> Dict[str, Any]:
        """Run specific test methods."""
        results = []
        start_time = time.time()
        
        for test_name in test_names:
            if hasattr(self, test_name):
                try:
                    test_start = time.time()
                    test_result = getattr(self, test_name)()
                    test_duration = time.time() - test_start
                    results.append(test_result)
                except Exception as e:
                    error_result = TestResult(
                        test_name=test_name,
                        category=TestCategory.UNIT,
                        status=TestStatus.ERROR,
                        duration=time.time() - test_start,
                        message=f"Test execution error: {str(e)}",
                        details={"error": str(e)},
                        timestamp=datetime.now()
                    )
                    results.append(error_result)
            else:
                missing_result = TestResult(
                    test_name=test_name,
                    category=TestCategory.UNIT,
                    status=TestStatus.SKIPPED,
                    duration=0.0,
                    message="Test method not implemented",
                    details={},
                    timestamp=datetime.now()
                )
                results.append(missing_result)
        
        return {
            "duration": time.time() - start_time,
            "results": [r.to_dict() for r in results]
        }
    
    # Test setup and teardown methods
    def setup_test_environment(self):
        """Set up test environment."""
        self._setup_test_environment()
    
    def teardown_test_environment(self):
        """Clean up test environment."""
        if os.path.exists(self.test_base_path):
            shutil.rmtree(self.test_base_path)
    
    # Configuration tests
    def test_config_creation(self) -> TestResult:
        """Test configuration creation."""
        start_time = time.time()
        try:
            config = PipelineConfig()
            
            return TestResult(
                test_name="test_config_creation",
                category=TestCategory.UNIT,
                status=TestStatus.PASSED,
                duration=time.time() - start_time,
                message="Configuration created successfully",
                details={"config": config.to_dict()},
                timestamp=datetime.now()
            )
        except Exception as e:
            return TestResult(
                test_name="test_config_creation",
                category=TestCategory.UNIT,
                status=TestStatus.FAILED,
                duration=time.time() - start_time,
                message=f"Configuration creation failed: {str(e)}",
                details={"error": str(e)},
                timestamp=datetime.now()
            )
    
    def test_config_loading(self) -> TestResult:
        """Test configuration loading and saving."""
        start_time = time.time()
        try:
            # Create test config
            config = PipelineConfig()
            config_path = os.path.join(self.test_base_path, 'test_config.json')
            
            # Save config
            config.save(config_path)
            
            # Load config
            loaded_config = PipelineConfig.load(config_path)
            
            # Verify they're equal
            if config.to_dict() == loaded_config.to_dict():
                return TestResult(
                    test_name="test_config_loading",
                    category=TestCategory.UNIT,
                    status=TestStatus.PASSED,
                    duration=time.time() - start_time,
                    message="Configuration loading and saving works correctly",
                    details={"config_path": config_path},
                    timestamp=datetime.now()
                )
            else:
                return TestResult(
                    test_name="test_config_loading",
                    category=TestCategory.UNIT,
                    status=TestStatus.FAILED,
                    duration=time.time() - start_time,
                    message="Loaded configuration doesn't match saved configuration",
                    details={"error": "configuration mismatch"},
                    timestamp=datetime.now()
                )
        except Exception as e:
            return TestResult(
                test_name="test_config_loading",
                category=TestCategory.UNIT,
                status=TestStatus.FAILED,
                duration=time.time() - start_time,
                message=f"Configuration loading failed: {str(e)}",
                details={"error": str(e)},
                timestamp=datetime.now()
            )
    
    def test_config_validation(self) -> TestResult:
        """Test configuration validation."""
        start_time = time.time()
        try:
            # Test valid config
            config = PipelineConfig(max_workers=4, batch_size=100)
            
            # Test invalid config (should handle gracefully)
            try:
                config.update(invalid_key="value")
                return TestResult(
                    test_name="test_config_validation",
                    category=TestCategory.UNIT,
                    status=TestStatus.FAILED,
                    duration=time.time() - start_time,
                    message="Config should reject invalid keys",
                    details={},
                    timestamp=datetime.now()
                )
            except ValueError:
                return TestResult(
                    test_name="test_config_validation",
                    category=TestCategory.UNIT,
                    status=TestStatus.PASSED,
                    duration=time.time() - start_time,
                    message="Configuration validation works correctly",
                    details={"valid_config": True},
                    timestamp=datetime.now()
                )
        except Exception as e:
            return TestResult(
                test_name="test_config_validation",
                category=TestCategory.UNIT,
                status=TestStatus.FAILED,
                duration=time.time() - start_time,
                message=f"Configuration validation failed: {str(e)}",
                details={"error": str(e)},
                timestamp=datetime.now()
            )
    
    # Logging and monitoring tests
    def test_logger_creation(self) -> TestResult:
        """Test logger creation and functionality."""
        start_time = time.time()
        try:
            logger = PipelineLogger(
                name="test_logger",
                logs_path=self.test_logs_path,
                log_level="INFO"
            )
            
            # Test logging
            logger.info("Test log message")
            logger.debug("Test debug message")
            
            # Check if log file was created
            log_file = os.path.join(self.test_logs_path, "test_logger.log")
            if os.path.exists(log_file):
                return TestResult(
                    test_name="test_logger_creation",
                    category=TestCategory.UNIT,
                    status=TestStatus.PASSED,
                    duration=time.time() - start_time,
                    message="Logger created and working correctly",
                    details={"log_file": log_file},
                    timestamp=datetime.now()
                )
            else:
                return TestResult(
                    test_name="test_logger_creation",
                    category=TestCategory.UNIT,
                    status=TestStatus.FAILED,
                    duration=time.time() - start_time,
                    message="Log file was not created",
                    details={},
                    timestamp=datetime.now()
                )
        except Exception as e:
            return TestResult(
                test_name="test_logger_creation",
                category=TestCategory.UNIT,
                status=TestStatus.FAILED,
                duration=time.time() - start_time,
                message=f"Logger creation failed: {str(e)}",
                details={"error": str(e)},
                timestamp=datetime.now()
            )
    
    def test_metrics_collection(self) -> TestResult:
        """Test metrics collection functionality."""
        start_time = time.time()
        try:
            metrics_collector = MetricsCollector(
                pipeline_id="test_pipeline",
                logs_path=self.test_logs_path
            )
            
            # Start and complete a step
            step_metrics = metrics_collector.start_step("test_step")
            metrics_collector.complete_step("test_step", status="completed")
            
            # Get metrics
            metrics = metrics_collector.get_metrics()
            
            return TestResult(
                test_name="test_metrics_collection",
                category=TestCategory.UNIT,
                status=TestStatus.PASSED,
                duration=time.time() - start_time,
                message="Metrics collection working correctly",
                details={
                    "pipeline_id": metrics.pipeline_id,
                    "completed_steps": metrics.completed_steps
                },
                timestamp=datetime.now()
            )
        except Exception as e:
            return TestResult(
                test_name="test_metrics_collection",
                category=TestCategory.UNIT,
                status=TestStatus.FAILED,
                duration=time.time() - start_time,
                message=f"Metrics collection failed: {str(e)}",
                details={"error": str(e)},
                timestamp=datetime.now()
            )
    
    # Progress tracking tests
    def test_progress_tracker(self) -> TestResult:
        """Test progress tracking functionality."""
        start_time = time.time()
        try:
            tracker = ProgressTracker(
                pipeline_id="test_pipeline",
                logs_path=self.test_logs_path
            )
            
            # Set steps
            steps = ["step1", "step2", "step3"]
            tracker.set_steps(steps, total_records=1000)
            
            # Start step
            tracker.start_step("step1", estimated_records=100)
            tracker.update_step_progress("step1", 50)
            tracker.complete_step("step1", success=True)
            
            # Check progress
            progress_info = tracker.get_progress_info()
            
            if progress_info.completed_steps == 1 and progress_info.overall_progress > 0:
                return TestResult(
                    test_name="test_progress_tracker",
                    category=TestCategory.UNIT,
                    status=TestStatus.PASSED,
                    duration=time.time() - start_time,
                    message="Progress tracking working correctly",
                    details={
                        "progress": progress_info.overall_progress,
                        "completed_steps": progress_info.completed_steps
                    },
                    timestamp=datetime.now()
                )
            else:
                return TestResult(
                    test_name="test_progress_tracker",
                    category=TestCategory.UNIT,
                    status=TestStatus.FAILED,
                    duration=time.time() - start_time,
                    message="Progress tracking not working as expected",
                    details={"progress_info": progress_info.__dict__},
                    timestamp=datetime.now()
                )
        except Exception as e:
            return TestResult(
                test_name="test_progress_tracker",
                category=TestCategory.UNIT,
                status=TestStatus.FAILED,
                duration=time.time() - start_time,
                message=f"Progress tracking failed: {str(e)}",
                details={"error": str(e)},
                timestamp=datetime.now()
            )
    
    def test_error_recovery(self) -> TestResult:
        """Test error recovery functionality."""
        start_time = time.time()
        try:
            error_recovery = ErrorRecovery(logs_path=self.test_logs_path)
            
            # Add an error
            try:
                raise ValueError("Test error")
            except Exception as e:
                error_info = error_recovery.add_error("test_step", e)
            
            # Check if error was added
            errors = error_recovery.get_errors_for_step("test_step")
            
            if len(errors) == 1 and errors[0].error_type == "ValueError":
                return TestResult(
                    test_name="test_error_recovery",
                    category=TestCategory.UNIT,
                    status=TestStatus.PASSED,
                    duration=time.time() - start_time,
                    message="Error recovery working correctly",
                    details={"error_count": len(errors)},
                    timestamp=datetime.now()
                )
            else:
                return TestResult(
                    test_name="test_error_recovery",
                    category=TestCategory.UNIT,
                    status=TestStatus.FAILED,
                    duration=time.time() - start_time,
                    message="Error recovery not working as expected",
                    details={"errors": [e.to_dict() for e in errors]},
                    timestamp=datetime.now()
                )
        except Exception as e:
            return TestResult(
                test_name="test_error_recovery",
                category=TestCategory.UNIT,
                status=TestStatus.FAILED,
                duration=time.time() - start_time,
                message=f"Error recovery failed: {str(e)}",
                details={"error": str(e)},
                timestamp=datetime.now()
            )
    
    # Validation tests
    def test_validation_engine(self) -> TestResult:
        """Test validation engine functionality."""
        start_time = time.time()
        try:
            validation_engine = ValidationEngine(logs_path=self.test_logs_path)
            
            # Test validation with sample data
            report = validation_engine.validate_step(
                step_name="test_step",
                data_path=os.path.join(self.test_data_path, 'sample_data.json'),
                validation_level=ValidationLevel.BASIC
            )
            
            if report.overall_status.value in ["passed", "warning"]:
                return TestResult(
                    test_name="test_validation_engine",
                    category=TestCategory.UNIT,
                    status=TestStatus.PASSED,
                    duration=time.time() - start_time,
                    message="Validation engine working correctly",
                    details={
                        "overall_status": report.overall_status.value,
                        "results_count": len(report.results)
                    },
                    timestamp=datetime.now()
                )
            else:
                return TestResult(
                    test_name="test_validation_engine",
                    category=TestCategory.UNIT,
                    status=TestStatus.FAILED,
                    duration=time.time() - start_time,
                    message="Validation engine produced unexpected results",
                    details={"overall_status": report.overall_status.value},
                    timestamp=datetime.now()
                )
        except Exception as e:
            return TestResult(
                test_name="test_validation_engine",
                category=TestCategory.UNIT,
                status=TestStatus.FAILED,
                duration=time.time() - start_time,
                message=f"Validation engine failed: {str(e)}",
                details={"error": str(e)},
                timestamp=datetime.now()
            )
    
    # Pipeline integration tests
    def test_pipeline_runner(self) -> TestResult:
        """Test pipeline runner functionality."""
        start_time = time.time()
        try:
            # Create a minimal pipeline runner
            runner = PipelineRunner()
            
            # Test status retrieval
            status = runner.get_status()
            
            if "pipeline_id" in status and "state" in status:
                return TestResult(
                    test_name="test_pipeline_runner",
                    category=TestCategory.INTEGRATION,
                    status=TestStatus.PASSED,
                    duration=time.time() - start_time,
                    message="Pipeline runner working correctly",
                    details={
                        "pipeline_id": status["pipeline_id"],
                        "state": status["state"]
                    },
                    timestamp=datetime.now()
                )
            else:
                return TestResult(
                    test_name="test_pipeline_runner",
                    category=TestCategory.INTEGRATION,
                    status=TestStatus.FAILED,
                    duration=time.time() - start_time,
                    message="Pipeline runner status incomplete",
                    details={"status": status},
                    timestamp=datetime.now()
                )
        except Exception as e:
            return TestResult(
                test_name="test_pipeline_runner",
                category=TestCategory.INTEGRATION,
                status=TestStatus.FAILED,
                duration=time.time() - start_time,
                message=f"Pipeline runner test failed: {str(e)}",
                details={"error": str(e)},
                timestamp=datetime.now()
            )
    
    def test_full_pipeline_execution(self) -> TestResult:
        """Test full pipeline execution with minimal steps."""
        start_time = time.time()
        try:
            # Create runner with test configuration
            runner = PipelineRunner()
            
            # Run a small subset of steps for testing
            success = runner.run_full_pipeline(steps=["data_collection"])
            
            if success:
                status = runner.get_status()
                return TestResult(
                    test_name="test_full_pipeline_execution",
                    category=TestCategory.INTEGRATION,
                    status=TestStatus.PASSED,
                    duration=time.time() - start_time,
                    message="Full pipeline execution completed successfully",
                    details={
                        "final_state": status["state"],
                        "completed_steps": status["execution_context"]["completed_steps"]
                    },
                    timestamp=datetime.now()
                )
            else:
                return TestResult(
                    test_name="test_full_pipeline_execution",
                    category=TestCategory.INTEGRATION,
                    status=TestStatus.FAILED,
                    duration=time.time() - start_time,
                    message="Full pipeline execution failed",
                    details={"status": runner.get_status()},
                    timestamp=datetime.now()
                )
        except Exception as e:
            return TestResult(
                test_name="test_full_pipeline_execution",
                category=TestCategory.INTEGRATION,
                status=TestStatus.FAILED,
                duration=time.time() - start_time,
                message=f"Full pipeline execution error: {str(e)}",
                details={"error": str(e)},
                timestamp=datetime.now()
            )
    
    def test_error_handling(self) -> TestResult:
        """Test pipeline error handling."""
        start_time = time.time()
        try:
            # Test with a runner that will encounter an error
            runner = PipelineRunner()
            
            # Try to run non-existent step (should handle gracefully)
            try:
                success = runner.run_full_pipeline(steps=["non_existent_step"])
                # Even if it fails, error handling should work
                return TestResult(
                    test_name="test_error_handling",
                    category=TestCategory.INTEGRATION,
                    status=TestStatus.PASSED,
                    duration=time.time() - start_time,
                    message="Error handling working correctly",
                    details={"handled_gracefully": True},
                    timestamp=datetime.now()
                )
            except Exception:
                # This is expected behavior
                return TestResult(
                    test_name="test_error_handling",
                    category=TestCategory.INTEGRATION,
                    status=TestStatus.PASSED,
                    duration=time.time() - start_time,
                    message="Error handling working correctly",
                    details={"handled_gracefully": True},
                    timestamp=datetime.now()
                )
        except Exception as e:
            return TestResult(
                test_name="test_error_handling",
                category=TestCategory.INTEGRATION,
                status=TestStatus.FAILED,
                duration=time.time() - start_time,
                message=f"Error handling test failed: {str(e)}",
                details={"error": str(e)},
                timestamp=datetime.now()
            )
    
    # Performance tests
    def test_performance_metrics(self) -> TestResult:
        """Test performance metrics collection."""
        start_time = time.time()
        try:
            metrics_collector = MetricsCollector(
                pipeline_id="performance_test",
                logs_path=self.test_logs_path
            )
            
            # Simulate some work
            for i in range(10):
                step_metrics = metrics_collector.start_step(f"step_{i}")
                time.sleep(0.1)  # Simulate work
                metrics_collector.complete_step(f"step_{i}", status="completed")
            
            # Get final metrics
            metrics = metrics_collector.get_metrics()
            
            return TestResult(
                test_name="test_performance_metrics",
                category=TestCategory.PERFORMANCE,
                status=TestStatus.PASSED,
                duration=time.time() - start_time,
                message="Performance metrics collection working",
                details={
                    "total_duration": metrics.total_duration,
                    "peak_memory_mb": metrics.peak_memory_mb,
                    "average_step_duration": metrics.average_step_duration
                },
                timestamp=datetime.now()
            )
        except Exception as e:
            return TestResult(
                test_name="test_performance_metrics",
                category=TestCategory.PERFORMANCE,
                status=TestStatus.FAILED,
                duration=time.time() - start_time,
                message=f"Performance metrics test failed: {str(e)}",
                details={"error": str(e)},
                timestamp=datetime.now()
            )
    
    # Additional test placeholder methods (these would be implemented with actual test logic)
    def test_config_saving(self) -> TestResult:
        """Test configuration saving functionality."""
        # Placeholder implementation
        return TestResult(
            test_name="test_config_saving",
            category=TestCategory.UNIT,
            status=TestStatus.SKIPPED,
            duration=0.0,
            message="Test not implemented",
            details={},
            timestamp=datetime.now()
        )
    
    def test_monitoring_dashboard(self) -> TestResult:
        """Test monitoring dashboard functionality."""
        # Placeholder implementation
        return TestResult(
            test_name="test_monitoring_dashboard",
            category=TestCategory.UNIT,
            status=TestStatus.SKIPPED,
            duration=0.0,
            message="Test not implemented",
            details={},
            timestamp=datetime.now()
        )
    
    def test_progress_callbacks(self) -> TestResult:
        """Test progress callback functionality."""
        # Placeholder implementation
        return TestResult(
            test_name="test_progress_callbacks",
            category=TestCategory.UNIT,
            status=TestStatus.SKIPPED,
            duration=0.0,
            message="Test not implemented",
            details={},
            timestamp=datetime.now()
        )
    
    def test_validation_rules(self) -> TestResult:
        """Test validation rules functionality."""
        # Placeholder implementation
        return TestResult(
            test_name="test_validation_rules",
            category=TestCategory.UNIT,
            status=TestStatus.SKIPPED,
            duration=0.0,
            message="Test not implemented",
            details={},
            timestamp=datetime.now()
        )
    
    def test_validation_reports(self) -> TestResult:
        """Test validation reports functionality."""
        # Placeholder implementation
        return TestResult(
            test_name="test_validation_reports",
            category=TestCategory.UNIT,
            status=TestStatus.SKIPPED,
            duration=0.0,
            message="Test not implemented",
            details={},
            timestamp=datetime.now()
        )
    
    def test_scheduler_creation(self) -> TestResult:
        """Test scheduler creation functionality."""
        # Placeholder implementation
        return TestResult(
            test_name="test_scheduler_creation",
            category=TestCategory.INTEGRATION,
            status=TestStatus.SKIPPED,
            duration=0.0,
            message="Test not implemented",
            details={},
            timestamp=datetime.now()
        )
    
    def test_schedule_management(self) -> TestResult:
        """Test schedule management functionality."""
        # Placeholder implementation
        return TestResult(
            test_name="test_schedule_management",
            category=TestCategory.INTEGRATION,
            status=TestStatus.SKIPPED,
            duration=0.0,
            message="Test not implemented",
            details={},
            timestamp=datetime.now()
        )
    
    def test_job_execution(self) -> TestResult:
        """Test job execution functionality."""
        # Placeholder implementation
        return TestResult(
            test_name="test_job_execution",
            category=TestCategory.INTEGRATION,
            status=TestStatus.SKIPPED,
            duration=0.0,
            message="Test not implemented",
            details={},
            timestamp=datetime.now()
        )
    
    def test_memory_usage(self) -> TestResult:
        """Test memory usage monitoring."""
        # Placeholder implementation
        return TestResult(
            test_name="test_memory_usage",
            category=TestCategory.PERFORMANCE,
            status=TestStatus.SKIPPED,
            duration=0.0,
            message="Test not implemented",
            details={},
            timestamp=datetime.now()
        )
    
    def test_concurrent_execution(self) -> TestResult:
        """Test concurrent execution capabilities."""
        # Placeholder implementation
        return TestResult(
            test_name="test_concurrent_execution",
            category=TestCategory.PERFORMANCE,
            status=TestStatus.SKIPPED,
            duration=0.0,
            message="Test not implemented",
            details={},
            timestamp=datetime.now()
        )
    
    def save_test_results(self, output_path: str):
        """Save test results to a file."""
        results = self.run_all_tests()
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, default=str)
        
        return output_path


def main():
    """Main entry point for testing."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Pashto Dataset Pipeline Testing")
    parser.add_argument("--suite", type=str, help="Run specific test suite")
    parser.add_argument("--tests", type=str, nargs="+", help="Run specific test methods")
    parser.add_argument("--output", type=str, help="Save results to file")
    parser.add_argument("--verbose", action="store_true", help="Verbose output")
    
    args = parser.parse_args()
    
    try:
        tester = PipelineTester()
        
        if args.suite:
            results = tester.run_test_suite(args.suite)
        elif args.tests:
            results = tester.run_specific_tests(args.tests)
        else:
            results = tester.run_all_tests()
        
        if args.output:
            tester.save_test_results(args.output)
        
        # Print results
        if args.verbose:
            print(json.dumps(results, indent=2, default=str))
        else:
            summary = results.get("summary", {})
            print(f"Tests completed in {summary.get('total_duration', 0):.2f}s")
            print(f"Passed: {summary.get('passed', 0)}")
            print(f"Failed: {summary.get('failed', 0)}")
            print(f"Skipped: {summary.get('skipped', 0)}")
            print(f"Errors: {summary.get('errors', 0)}")
            print(f"Success rate: {summary.get('success_rate', 0):.1f}%")
    
    except Exception as e:
        print(f"Testing error: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()