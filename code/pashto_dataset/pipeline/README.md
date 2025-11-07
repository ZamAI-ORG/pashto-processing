# Pashto Dataset Pipeline Orchestration System

A comprehensive pipeline orchestration system that automates the entire dataset creation process with advanced features including configuration management, logging and monitoring, progress tracking, error recovery, pipeline scheduling, and validation systems.

## Overview

This system provides a complete solution for orchestrating Pashto dataset processing pipelines with the following key components:

- **Configuration Management**: Centralized configuration system with flexible settings
- **Logging & Monitoring**: Comprehensive logging with real-time monitoring and metrics collection
- **Progress Tracking**: Real-time progress tracking with visual feedback
- **Error Recovery**: Intelligent error handling with retry mechanisms and recovery strategies
- **Pipeline Scheduling**: Automated scheduling with cron-like expressions and dependency management
- **Validation System**: Multi-level validation with customizable rules and reporting
- **Testing & Validation**: Comprehensive testing framework for pipeline components

## Architecture

The pipeline system follows a modular architecture with the following main components:

```
pashto_dataset/pipeline/
├── __init__.py                 # Package initialization
├── config.py                  # Configuration management
├── logging_monitoring.py      # Logging and monitoring
├── progress_error_recovery.py # Progress tracking and error recovery
├── validation.py              # Validation system
├── scheduler.py               # Pipeline scheduling
├── testing.py                 # Testing framework
├── main.py                    # Main pipeline runner
└── README.md                  # This file
```

## Quick Start

### Basic Usage

```python
from pashto_dataset.pipeline import PipelineRunner

# Initialize the pipeline runner
runner = PipelineRunner()

# Run the complete pipeline
success = runner.run_full_pipeline()

# Check pipeline status
status = runner.get_status()
print(f"Pipeline state: {status['state']}")
```

### Advanced Usage with Custom Configuration

```python
from pashto_dataset.pipeline import PipelineRunner, PipelineConfig

# Create custom configuration
config = PipelineConfig()
config.max_workers = 8
config.validation_level = "strict"
config.log_level = "DEBUG"

# Initialize with custom config
runner = PipelineRunner()
runner.pipeline_config.update(
    max_workers=8,
    validation_level="strict",
    log_level="DEBUG"
)

# Run specific steps
success = runner.run_full_pipeline(steps=["data_collection", "data_cleaning"])
```

### Scheduled Execution

```python
from pashto_dataset.pipeline import PipelineScheduler, ScheduleConfig, ScheduleType

# Initialize scheduler
scheduler = PipelineScheduler("/path/to/pipeline")

# Create daily schedule
schedule = ScheduleConfig(
    schedule_id="daily_pipeline",
    name="Daily Pipeline Run",
    description="Run pipeline daily at 2 AM",
    schedule_type=ScheduleType.DAILY,
    expression="02:00",
    timezone="UTC"
)

# Add and start schedule
scheduler.add_schedule(schedule)
scheduler.start_scheduler()
```

## Configuration System

### Pipeline Configuration

The `PipelineConfig` class provides comprehensive configuration options:

```python
from pashto_dataset.pipeline import PipelineConfig

config = PipelineConfig(
    pipeline_name="my_pashto_pipeline",
    max_workers=4,
    batch_size=100,
    validation_level="standard",
    enable_scheduling=True,
    log_level="INFO"
)
```

**Key Configuration Options:**

- **Processing Settings**: `max_workers`, `chunk_size`, `batch_size`, `timeout_seconds`
- **Retry Settings**: `max_retries`, `retry_delay`, `exponential_backoff`
- **Validation Settings**: `validation_strict`, `auto_validation`, `validation_level`
- **Monitoring Settings**: `enable_monitoring`, `log_level`, `log_format`
- **Scheduling Settings**: `enable_scheduling`, `schedule_expression`, `timezone`
- **Performance Settings**: `memory_limit_mb`, `disk_limit_gb`, `cpu_limit_percent`

### Step Configuration

Individual steps can be configured with:

```python
from pashto_dataset.pipeline import PipelineStepConfig

step_config = PipelineStepConfig(
    step_name="data_collection",
    enabled=True,
    dependencies=[],
    timeout=3600,
    retry_count=3,
    parallel=False,
    validation_required=True,
    custom_config={"source": "web", "max_records": 10000}
)
```

## Monitoring and Logging

### Real-time Monitoring

The system provides comprehensive monitoring capabilities:

```python
from pashto_dataset.pipeline import MonitoringDashboard

# Access monitoring dashboard
dashboard = runner.monitoring_dashboard

# Get real-time status
status_summary = dashboard.get_status_summary()
print(f"Progress: {status_summary['progress']['percentage']:.1f}%")
print(f"Current Step: {status_summary['current_step']}")
print(f"Memory Usage: {status_summary['resources']['memory_mb']} MB")
```

### Logging Configuration

```python
from pashto_dataset.pipeline import PipelineLogger

logger = PipelineLogger(
    name="pashto_pipeline",
    logs_path="/path/to/logs",
    log_level="INFO",
    log_format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    log_rotation="daily",
    log_retention_days=30
)

# Use logger
logger.info("Pipeline started")
logger.warning("Low memory detected")
logger.error("Step failed: data_collection")
```

## Progress Tracking

### Progress Callbacks

Register callbacks for real-time progress updates:

```python
def progress_callback(progress_info):
    print(f"Progress: {progress_info.overall_progress:.1f}%")
    print(f"Current step: {progress_info.current_step}")
    print(f"Records processed: {progress_info.records_processed}")

# Register callback
runner.progress_tracker.register_callback(progress_callback)
```

### Progress Information

The `ProgressInfo` object provides detailed progress data:

- `overall_progress`: Overall pipeline progress (0-100%)
- `step_progress`: Current step progress (0-100%)
- `current_step`: Name of the current step
- `total_steps`: Total number of steps
- `completed_steps`: Number of completed steps
- `estimated_remaining_time`: Estimated time to completion
- `current_rate`: Current processing rate (records/second)

## Error Recovery

### Automatic Error Handling

The system includes sophisticated error recovery mechanisms:

```python
from pashto_dataset.pipeline import ErrorRecovery

# Access error recovery
error_recovery = runner.error_recovery

# Check if step can be retried
can_retry = error_recovery.can_retry(
    step_name="data_collection",
    max_retries=3,
    retry_delay=5.0,
    exponential_backoff=True
)

# Get recovery suggestions
suggestions = error_recovery.get_recovery_suggestions("data_collection")
for suggestion in suggestions:
    print(f"Recovery suggestion: {suggestion}")
```

### Custom Recovery Strategies

Register custom recovery strategies:

```python
def network_recovery_strategy(error_info):
    # Implement custom recovery logic
    return True  # Recovery successful

# Register strategy
error_recovery.register_recovery_strategy("ConnectionError", network_recovery_strategy)
```

## Validation System

### Validation Levels

The system supports three validation levels:

- **Basic**: Essential file and format checks
- **Standard**: Comprehensive data quality validation
- **Strict**: Full validation with language detection and consistency checks

### Running Validations

```python
from pashto_dataset.pipeline import ValidationEngine, ValidationLevel

# Initialize validation engine
validator = ValidationEngine(logs_path="/path/to/logs")

# Run validation
report = validator.validate_step(
    step_name="data_collection",
    data_path="/path/to/data",
    validation_level=ValidationLevel.STANDARD
)

# Check results
if report.overall_status.value == "failed":
    print("Validation failed!")
    for result in report.results:
        if result.status.value == "failed":
            print(f"Failed rule: {result.rule_name} - {result.message}")
```

### Custom Validation Rules

Create custom validation rules:

```python
from pashto_dataset.pipeline import ValidationRule

def custom_validation(data_path, config, **kwargs):
    # Custom validation logic
    return True, "Custom validation passed", {"custom_data": "value"}

# Register rule
rule = ValidationRule(
    name="custom_check",
    description="Custom validation check",
    level=ValidationLevel.STANDARD,
    function=custom_validation,
    custom_config={"threshold": 0.95}
)

validator.register_rule(rule)
```

## Pipeline Scheduling

### Schedule Types

- **Once**: Run once at a specific time
- **Daily**: Run daily at specified time
- **Weekly**: Run weekly on specified day/time
- **Monthly**: Run monthly on specified day/time
- **Cron**: Run based on cron expression
- **Interval**: Run at regular intervals

### Schedule Management

```python
# Create weekly schedule
weekly_schedule = ScheduleConfig(
    schedule_id="weekly_pipeline",
    name="Weekly Dataset Update",
    description="Update dataset every Monday",
    schedule_type=ScheduleType.WEEKLY,
    expression="monday 03:00",
    timezone="UTC",
    max_runs=52  # One year of weekly runs
)

# Add schedule
scheduler.add_schedule(weekly_schedule)

# List schedules
schedules = scheduler.list_schedules()
for schedule in schedules:
    print(f"Schedule: {schedule.name} - Next run: {schedule.next_run}")
```

## Testing Framework

### Running Tests

```python
from pashto_dataset.pipeline import PipelineTester

# Initialize tester
tester = PipelineTester()

# Run all tests
results = tester.run_all_tests()

# Run specific test suite
suite_results = tester.run_test_suite("integration_tests")

# Run specific tests
test_results = tester.run_specific_tests(["test_config_creation", "test_logger"])
```

### Test Categories

- **Unit Tests**: Individual component testing
- **Integration Tests**: Component interaction testing
- **System Tests**: Full pipeline testing
- **Performance Tests**: Performance and resource usage testing

### Command Line Testing

```bash
# Run all tests
python -m pashto_dataset.pipeline.testing

# Run specific suite
python -m pashto_dataset.pipeline.testing --suite integration_tests

# Run specific tests
python -m pashto_dataset.pipeline.testing --tests test_config_creation test_logger

# Save results to file
python -m pashto_dataset.pipeline.testing --output test_results.json

# Verbose output
python -m pashto_dataset.pipeline.testing --verbose
```

## Command Line Interface

### Pipeline Runner

```bash
# Run complete pipeline
python -m pashto_dataset.pipeline.main

# Run with custom configuration
python -m pashto_dataset.pipeline.main --config custom_config.json

# Run specific steps
python -m pashto_dataset.pipeline.main --steps data_collection data_cleaning

# Show pipeline status
python -m pashto_dataset.pipeline.main --status

# Run tests
python -m pashto_dataset.pipeline.main --test
```

## Directory Structure

The pipeline creates and manages the following directory structure:

```
pashto_dataset/
├── pipeline_config.json          # Main configuration
├── step_configs.json            # Step configurations
├── schedules.json               # Schedule configurations
├── scheduler_state.json         # Scheduler state
├── data/                        # Data files
│   ├── raw/                    # Raw data
│   └── processed/              # Processed data
├── output/                     # Final output
├── logs/                       # Log files
│   ├── pashto_pipeline.log     # Main log
│   ├── pashto_pipeline_errors.log  # Error log
│   ├── validations/            # Validation reports
│   ├── steps/                  # Step metrics
│   └── {pipeline_id}_metrics.json  # Pipeline metrics
└── {pipeline_id}_progress.json  # Progress state
```

## Error Handling

The system provides comprehensive error handling at multiple levels:

### Step-Level Errors

- Automatic retry with configurable backoff
- Error logging and metrics collection
- Recovery strategy execution
- Graceful degradation

### Pipeline-Level Errors

- Step dependency management
- Partial completion handling
- Rollback capabilities
- State preservation

### System-Level Errors

- Resource limit monitoring
- Memory and disk space checks
- Process monitoring and cleanup
- Signal handling for graceful shutdown

## Performance Monitoring

### Resource Usage Tracking

The system monitors and logs:

- **Memory Usage**: Peak and current memory consumption
- **CPU Usage**: CPU utilization during execution
- **Disk Usage**: Disk space consumption
- **Processing Rate**: Records processed per second
- **Step Duration**: Individual step execution times

### Performance Metrics

```python
# Access metrics
metrics = runner.metrics_collector.get_metrics()

print(f"Peak memory: {metrics.peak_memory_mb:.1f} MB")
print(f"Peak CPU: {metrics.peak_cpu_percent:.1f}%")
print(f"Average step duration: {metrics.average_step_duration:.2f}s")
print(f"Slowest step: {metrics.slowest_step}")
print(f"Fastest step: {metrics.fastest_step}")
```

## Best Practices

### Configuration Management

1. **Use environment-specific configs**: Create separate configurations for dev, staging, and production
2. **Version control configurations**: Track configuration changes in version control
3. **Validate configurations**: Use the validation system to ensure config correctness
4. **Document custom settings**: Maintain documentation for custom configuration options

### Error Handling

1. **Implement recovery strategies**: Provide custom recovery logic for expected error types
2. **Log detailed error information**: Include context and debugging information
3. **Use appropriate retry policies**: Configure exponential backoff for transient errors
4. **Monitor error patterns**: Track recurring errors for system improvement

### Performance Optimization

1. **Optimize worker counts**: Configure based on available CPU cores and memory
2. **Use appropriate batch sizes**: Balance memory usage with processing efficiency
3. **Monitor resource usage**: Set appropriate resource limits
4. **Profile step performance**: Identify and optimize bottlenecks

### Testing

1. **Run tests regularly**: Include in CI/CD pipeline
2. **Test with realistic data**: Use representative test datasets
3. **Monitor test coverage**: Ensure all components are tested
4. **Performance test regularly**: Monitor performance regressions

## Troubleshooting

### Common Issues

**Pipeline fails to start**
- Check configuration file syntax
- Verify directory permissions
- Ensure all dependencies are installed
- Check log files for detailed error messages

**Steps failing repeatedly**
- Review error messages in logs
- Check input data quality
- Verify step dependencies
- Examine resource usage (memory/disk)

**Performance issues**
- Monitor resource usage patterns
- Adjust worker counts and batch sizes
- Check for I/O bottlenecks
- Review step implementation efficiency

**Validation failures**
- Review validation reports for specific failures
- Check data format and encoding
- Verify required fields and metadata
- Adjust validation rules if necessary

### Log Analysis

Key log files to monitor:

- `pashto_pipeline.log`: Main execution log
- `pashto_pipeline_errors.log`: Error-specific log
- `validations/`: Validation reports
- `steps/`: Individual step metrics

### Monitoring Dashboard

Use the monitoring dashboard for real-time insights:

```python
# Get current status
status = runner.monitoring_dashboard.get_status_summary()
print(json.dumps(status, indent=2))
```

## API Reference

### Main Classes

#### PipelineRunner
- `__init__(config_path=None)`: Initialize pipeline runner
- `run_full_pipeline(steps=None)`: Execute pipeline
- `get_status()`: Get current pipeline status
- `stop()`: Stop pipeline execution

#### PipelineConfig
- Configuration class with all pipeline settings
- Methods: `save()`, `load()`, `update()`, `to_dict()`

#### ConfigManager
- `load_pipeline_config()`: Load main configuration
- `load_step_configs()`: Load step configurations
- `save_step_configs()`: Save step configurations

#### PipelineScheduler
- `add_schedule()`: Add new schedule
- `start_scheduler()`: Start scheduler
- `stop_scheduler()`: Stop scheduler
- `list_schedules()`: List all schedules

#### PipelineTester
- `run_all_tests()`: Run all test suites
- `run_test_suite()`: Run specific test suite
- `run_specific_tests()`: Run specific test methods

## Contributing

When contributing to the pipeline system:

1. **Follow coding standards**: Use consistent code formatting
2. **Add tests**: Include tests for new functionality
3. **Update documentation**: Update README and docstrings
4. **Test thoroughly**: Run full test suite before submitting
5. **Consider performance**: Ensure changes don't negatively impact performance

## License

This pipeline orchestration system is part of the Pashto dataset processing project.

## Support

For questions, issues, or contributions:

1. Check existing documentation
2. Review log files for error details
3. Run tests to isolate issues
4. Create detailed bug reports with logs and configuration
5. Include steps to reproduce issues

---

**Note**: This system is designed to be extensible and configurable. Most behaviors can be customized through configuration files or by implementing custom components following the established patterns.