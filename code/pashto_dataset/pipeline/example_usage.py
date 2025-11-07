"""
Example usage of the Pashto Dataset Pipeline Orchestration System.

This script demonstrates how to use the complete pipeline system with all features:
- Configuration management
- Pipeline execution
- Scheduling
- Monitoring
- Error handling
- Testing
"""

import os
import sys
import time
import json
import argparse
from pathlib import Path

# Add the parent directory to the path so we can import the pipeline
sys.path.insert(0, str(Path(__file__).parent))

from pashto_dataset.pipeline import (
    PipelineRunner, 
    PipelineConfig, 
    PipelineScheduler, 
    ScheduleConfig, 
    ScheduleType,
    PipelineTester,
    TestResult
)


def create_example_config():
    """Create an example pipeline configuration."""
    config = PipelineConfig(
        pipeline_name="pashto_dataset_example",
        pipeline_version="1.0.0",
        base_path="/workspace/code/pashto_dataset",
        
        # Processing settings
        max_workers=4,
        chunk_size=1000,
        batch_size=100,
        timeout_seconds=3600,
        
        # Retry settings
        max_retries=3,
        retry_delay=2.0,
        exponential_backoff=True,
        
        # Validation settings
        validation_level="standard",
        validation_strict=True,
        auto_validation=True,
        
        # Monitoring settings
        enable_monitoring=True,
        log_level="INFO",
        log_format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        log_retention_days=7,
        
        # Performance settings
        memory_limit_mb=2048,
        disk_limit_gb=5,
        cpu_limit_percent=80
    )
    
    return config


def setup_example_environment():
    """Set up example environment with sample data."""
    print("Setting up example environment...")
    
    # Create directories
    base_path = "/workspace/code/pashto_dataset"
    dirs = ['data/raw', 'data/processed', 'output', 'logs', 'tests']
    
    for dir_path in dirs:
        full_path = os.path.join(base_path, dir_path)
        os.makedirs(full_path, exist_ok=True)
        print(f"Created directory: {full_path}")
    
    # Create sample data
    sample_data = [
        {"id": 1, "text": "سلام نړی", "language": "pashto", "source": "web"},
        {"id": 2, "text": "Hello world", "language": "english", "source": "web"},
        {"id": 3, "text": "دا یو ښه مثال دی", "language": "pashto", "source": "book"},
        {"id": 4, "text": "This is a good example", "language": "english", "source": "book"},
    ]
    
    # Save sample data
    sample_file = os.path.join(base_path, "data/raw/sample_data.json")
    with open(sample_file, 'w', encoding='utf-8') as f:
        json.dump(sample_data, f, ensure_ascii=False, indent=2)
    
    print(f"Created sample data file: {sample_file}")
    return sample_file


def demonstrate_basic_pipeline():
    """Demonstrate basic pipeline functionality."""
    print("\n" + "="*60)
    print("DEMONSTRATING BASIC PIPELINE FUNCTIONALITY")
    print("="*60)
    
    try:
        # Set up environment
        setup_example_environment()
        
        # Create and save configuration
        config = create_example_config()
        config_file = os.path.join(config.base_path, "example_config.json")
        config.save(config_file)
        print(f"Saved configuration to: {config_file}")
        
        # Initialize pipeline runner
        print("\nInitializing pipeline runner...")
        runner = PipelineRunner(config_path=config_file)
        
        # Show initial status
        print("\nInitial pipeline status:")
        status = runner.get_status()
        print(f"Pipeline ID: {status['pipeline_id']}")
        print(f"State: {status['state']}")
        
        # Run a small subset of steps for demonstration
        print("\nRunning pipeline with selected steps...")
        steps_to_run = ["data_collection", "data_cleaning"]
        
        success = runner.run_full_pipeline(steps=steps_to_run)
        
        if success:
            print("✅ Pipeline completed successfully!")
        else:
            print("❌ Pipeline failed!")
        
        # Show final status
        print("\nFinal pipeline status:")
        final_status = runner.get_status()
        print(f"State: {final_status['state']}")
        print(f"Completed steps: {final_status['execution_context']['completed_steps']}")
        print(f"Failed steps: {final_status['execution_context']['failed_steps']}")
        print(f"Total errors: {final_status['execution_context']['error_count']}")
        
        # Show metrics
        metrics = final_status['metrics']
        print(f"\nPerformance metrics:")
        print(f"Peak memory usage: {metrics['peak_memory_mb']:.1f} MB")
        print(f"Peak CPU usage: {metrics['peak_cpu_percent']:.1f}%")
        
        return True
        
    except Exception as e:
        print(f"❌ Error in basic pipeline demonstration: {str(e)}")
        return False


def demonstrate_monitoring():
    """Demonstrate monitoring and logging features."""
    print("\n" + "="*60)
    print("DEMONSTRATING MONITORING AND LOGGING")
    print("="*60)
    
    try:
        # Initialize pipeline with monitoring enabled
        config = create_example_config()
        config.enable_monitoring = True
        config.log_level = "DEBUG"
        
        runner = PipelineRunner()
        runner.pipeline_config = config
        
        # Register progress callback
        def progress_callback(progress_info):
            print(f"Progress: {progress_info.overall_progress:.1f}% - "
                  f"Step: {progress_info.current_step}")
        
        runner.progress_tracker.register_callback(progress_callback)
        
        # Run with monitoring
        print("Running pipeline with monitoring enabled...")
        runner.run_full_pipeline(steps=["data_collection"])
        
        # Show monitoring results
        dashboard = runner.monitoring_dashboard
        status_summary = dashboard.get_status_summary()
        
        print("\nMonitoring results:")
        print(f"Pipeline status: {status_summary}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error in monitoring demonstration: {str(e)}")
        return False


def demonstrate_scheduling():
    """Demonstrate pipeline scheduling."""
    print("\n" + "="*60)
    print("DEMONSTRATING PIPELINE SCHEDULING")
    print("="*60)
    
    try:
        # Initialize scheduler
        base_path = "/workspace/code/pashto_dataset"
        scheduler = PipelineScheduler(base_path)
        
        # Create a daily schedule
        daily_schedule = ScheduleConfig(
            schedule_id="daily_example",
            name="Daily Pipeline Example",
            description="Run pipeline daily for demonstration",
            schedule_type=ScheduleType.DAILY,
            expression="15:30",  # 3:30 PM
            timezone="UTC",
            enabled=True,
            max_runs=3
        )
        
        # Add schedule
        print("Adding daily schedule...")
        scheduler.add_schedule(daily_schedule)
        
        # List schedules
        schedules = scheduler.list_schedules()
        print(f"\nCurrent schedules ({len(schedules)}):")
        for schedule in schedules:
            print(f"- {schedule.name}")
            print(f"  Type: {schedule.schedule_type.value}")
            print(f"  Expression: {schedule.expression}")
            print(f"  Next run: {schedule.next_run}")
            print(f"  Enabled: {schedule.enabled}")
        
        # Show next runs
        next_runs = scheduler.get_next_runs(hours=24)
        print(f"\nNext runs in next 24 hours:")
        for schedule_id, run_time in next_runs.items():
            print(f"- {schedule_id}: {run_time}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error in scheduling demonstration: {str(e)}")
        return False


def demonstrate_testing():
    """Demonstrate testing framework."""
    print("\n" + "="*60)
    print("DEMONSTRATING TESTING FRAMEWORK")
    print("="*60)
    
    try:
        # Initialize tester
        tester = PipelineTester()
        
        # Run specific tests
        print("Running configuration tests...")
        config_results = tester.run_test_suite("config_tests")
        print(f"Config tests - Passed: {config_results['passed']}, "
              f"Failed: {config_results['failed']}, "
              f"Skipped: {config_results['skipped']}")
        
        print("\nRunning logging tests...")
        logging_results = tester.run_test_suite("logging_tests")
        print(f"Logging tests - Passed: {logging_results['passed']}, "
              f"Failed: {logging_results['failed']}, "
              f"Skipped: {logging_results['skipped']}")
        
        # Run individual tests
        print("\nRunning individual tests...")
        individual_results = tester.run_specific_tests([
            "test_config_creation", 
            "test_logger_creation", 
            "test_progress_tracker"
        ])
        
        print(f"Individual tests - Results: {len(individual_results['results'])}")
        for result in individual_results['results']:
            print(f"- {result['test_name']}: {result['status']} ({result['duration']:.2f}s)")
        
        # Save test results
        results_file = os.path.join(base_path, "test_results.json")
        tester.save_test_results(results_file)
        print(f"\nTest results saved to: {results_file}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error in testing demonstration: {str(e)}")
        return False


def demonstrate_error_handling():
    """Demonstrate error handling and recovery."""
    print("\n" + "="*60)
    print("DEMONSTRATING ERROR HANDLING AND RECOVERY")
    print("="*60)
    
    try:
        # Initialize pipeline
        runner = PipelineRunner()
        
        # Access error recovery system
        error_recovery = runner.error_recovery
        
        # Simulate an error
        try:
            raise ValueError("Simulated error for testing")
        except Exception as e:
            print("Adding simulated error...")
            error_info = error_recovery.add_error(
                step_name="test_step", 
                error=e,
                is_recoverable=True,
                recovery_suggestion="Check input data format and try again"
            )
            print(f"Error added: {error_info.error_type} - {error_info.error_message}")
        
        # Test retry logic
        can_retry = error_recovery.can_retry(
            step_name="test_step",
            max_retries=3,
            retry_delay=1.0
        )
        print(f"Can retry step: {can_retry}")
        
        # Increment retry count
        error_recovery.increment_retry_count("test_step")
        
        # Get errors for step
        errors = error_recovery.get_errors_for_step("test_step")
        print(f"Errors for test_step: {len(errors)}")
        for error in errors:
            print(f"- {error.error_type} (retry count: {error.retry_count})")
        
        # Get recovery suggestions
        suggestions = error_recovery.get_recovery_suggestions("test_step")
        print(f"Recovery suggestions: {suggestions}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error in error handling demonstration: {str(e)}")
        return False


def main():
    """Main function to run all demonstrations."""
    parser = argparse.ArgumentParser(description="Pashto Dataset Pipeline Example")
    parser.add_argument("--demo", type=str, choices=[
        "basic", "monitoring", "scheduling", "testing", "error", "all"
    ], default="all", help="Which demonstration to run")
    parser.add_argument("--output", type=str, help="Output directory for results")
    
    args = parser.parse_args()
    
    # Set output directory
    global base_path
    base_path = args.output or "/workspace/code/pashto_dataset"
    os.makedirs(base_path, exist_ok=True)
    
    print("Pashto Dataset Pipeline Orchestration System")
    print("=" * 60)
    print(f"Base path: {base_path}")
    print(f"Demo: {args.demo}")
    print()
    
    # Run demonstrations
    success_count = 0
    total_count = 0
    
    if args.demo in ["all", "basic"]:
        total_count += 1
        if demonstrate_basic_pipeline():
            success_count += 1
    
    if args.demo in ["all", "monitoring"]:
        total_count += 1
        if demonstrate_monitoring():
            success_count += 1
    
    if args.demo in ["all", "scheduling"]:
        total_count += 1
        if demonstrate_scheduling():
            success_count += 1
    
    if args.demo in ["all", "testing"]:
        total_count += 1
        if demonstrate_testing():
            success_count += 1
    
    if args.demo in ["all", "error"]:
        total_count += 1
        if demonstrate_error_handling():
            success_count += 1
    
    # Summary
    print("\n" + "="*60)
    print("DEMONSTRATION SUMMARY")
    print("="*60)
    print(f"Completed: {success_count}/{total_count} demonstrations")
    print(f"Success rate: {success_count/total_count*100:.1f}%" if total_count > 0 else "No demonstrations run")
    
    if success_count == total_count:
        print("🎉 All demonstrations completed successfully!")
        return 0
    else:
        print("⚠️  Some demonstrations failed. Check the output above for details.")
        return 1


if __name__ == "__main__":
    sys.exit(main())