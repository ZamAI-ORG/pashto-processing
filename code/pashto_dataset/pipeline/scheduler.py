"""
Pipeline scheduling system for the Pashto dataset pipeline.
"""

import os
import time
import json
import threading
import schedule
from typing import Dict, List, Optional, Callable, Any
from datetime import datetime, timedelta
from pathlib import Path
from dataclasses import dataclass, asdict
from enum import Enum
import subprocess
import signal


class ScheduleStatus(Enum):
    """Schedule status."""
    ACTIVE = "active"
    PAUSED = "paused"
    DISABLED = "disabled"
    RUNNING = "running"
    FAILED = "failed"


class ScheduleType(Enum):
    """Schedule type."""
    ONCE = "once"
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    CRON = "cron"
    INTERVAL = "interval"


@dataclass
class ScheduleConfig:
    """Pipeline schedule configuration."""
    schedule_id: str
    name: str
    description: str
    schedule_type: ScheduleType
    expression: str  # cron expression, interval, or time string
    timezone: str = "UTC"
    enabled: bool = True
    max_runs: Optional[int] = None  # None for unlimited
    run_count: int = 0
    last_run: Optional[datetime] = None
    next_run: Optional[datetime] = None
    status: ScheduleStatus = ScheduleStatus.ACTIVE
    config_path: str = None
    parameters: Dict[str, Any] = None
    notification_config: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.parameters is None:
            self.parameters = {}
        if self.notification_config is None:
            self.notification_config = {}
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        schedule_dict = asdict(self)
        schedule_dict['schedule_type'] = self.schedule_type.value
        schedule_dict['status'] = self.status.value
        
        # Convert datetime objects
        for key, value in schedule_dict.items():
            if isinstance(value, datetime):
                schedule_dict[key] = value.isoformat()
        
        return schedule_dict
    
    @classmethod
    def from_dict(cls, schedule_dict: Dict[str, Any]) -> 'ScheduleConfig':
        """Create from dictionary."""
        # Convert strings back to enums and datetime
        schedule_dict['schedule_type'] = ScheduleType(schedule_dict['schedule_type'])
        schedule_dict['status'] = ScheduleStatus(schedule_dict['status'])
        
        for key, value in schedule_dict.items():
            if key in ['last_run', 'next_run'] and isinstance(value, str):
                schedule_dict[key] = datetime.fromisoformat(value)
        
        return cls(**schedule_dict)


class PipelineScheduler:
    """Pipeline scheduling system."""
    
    def __init__(self, base_path: str):
        self.base_path = Path(base_path)
        self.schedules_file = self.base_path / "schedules.json"
        self.scheduler_state_file = self.base_path / "scheduler_state.json"
        
        self.schedules: Dict[str, ScheduleConfig] = {}
        self.active_jobs: Dict[str, Any] = {}
        self.is_running = False
        self.scheduler_thread: Optional[threading.Thread] = None
        
        # Notification handlers
        self.notification_handlers: Dict[str, Callable] = {}
        
        self._load_schedules()
        self._setup_signal_handlers()
    
    def register_notification_handler(self, event_type: str, handler: Callable):
        """Register a notification handler."""
        self.notification_handlers[event_type] = handler
    
    def add_schedule(self, schedule_config: ScheduleConfig):
        """Add a new schedule."""
        self.schedules[schedule_config.schedule_id] = schedule_config
        self._save_schedules()
        
        if schedule_config.enabled:
            self._activate_schedule(schedule_config)
        
        self._notify("schedule_added", {
            "schedule_id": schedule_config.schedule_id,
            "name": schedule_config.name
        })
    
    def remove_schedule(self, schedule_id: str):
        """Remove a schedule."""
        if schedule_id in self.schedules:
            schedule_config = self.schedules[schedule_id]
            self._deactivate_schedule(schedule_config)
            del self.schedules[schedule_id]
            self._save_schedules()
            
            self._notify("schedule_removed", {
                "schedule_id": schedule_id,
                "name": schedule_config.name
            })
    
    def update_schedule(self, schedule_id: str, **kwargs):
        """Update a schedule."""
        if schedule_id not in self.schedules:
            raise ValueError(f"Schedule not found: {schedule_id}")
        
        schedule_config = self.schedules[schedule_id]
        
        # Update fields
        for key, value in kwargs.items():
            if hasattr(schedule_config, key):
                setattr(schedule_config, key, value)
        
        # Reactivate if enabled
        if schedule_config.enabled:
            self._deactivate_schedule(schedule_config)
            self._activate_schedule(schedule_config)
        
        self._save_schedules()
        self._notify("schedule_updated", {
            "schedule_id": schedule_id,
            "changes": kwargs
        })
    
    def pause_schedule(self, schedule_id: str):
        """Pause a schedule."""
        if schedule_id in self.schedules:
            schedule_config = self.schedules[schedule_id]
            schedule_config.status = ScheduleStatus.PAUSED
            self._deactivate_schedule(schedule_config)
            self._save_schedules()
            
            self._notify("schedule_paused", {"schedule_id": schedule_id})
    
    def resume_schedule(self, schedule_id: str):
        """Resume a schedule."""
        if schedule_id in self.schedules:
            schedule_config = self.schedules[schedule_id]
            schedule_config.status = ScheduleStatus.ACTIVE
            if schedule_config.enabled:
                self._activate_schedule(schedule_config)
            self._save_schedules()
            
            self._notify("schedule_resumed", {"schedule_id": schedule_id})
    
    def start_scheduler(self):
        """Start the scheduler."""
        if self.is_running:
            return
        
        self.is_running = True
        self.scheduler_thread = threading.Thread(target=self._run_scheduler, daemon=True)
        self.scheduler_thread.start()
        
        self._notify("scheduler_started", {"timestamp": datetime.now().isoformat()})
    
    def stop_scheduler(self):
        """Stop the scheduler."""
        if not self.is_running:
            return
        
        self.is_running = False
        
        # Stop all active jobs
        for schedule_id, job_info in self.active_jobs.items():
            self._stop_job(schedule_id, job_info)
        
        self.active_jobs.clear()
        
        if self.scheduler_thread and self.scheduler_thread.is_alive():
            self.scheduler_thread.join(timeout=5)
        
        self._notify("scheduler_stopped", {"timestamp": datetime.now().isoformat()})
    
    def get_schedule(self, schedule_id: str) -> Optional[ScheduleConfig]:
        """Get a schedule by ID."""
        return self.schedules.get(schedule_id)
    
    def list_schedules(self, status: ScheduleStatus = None) -> List[ScheduleConfig]:
        """List all schedules."""
        schedules = list(self.schedules.values())
        if status:
            schedules = [s for s in schedules if s.status == status]
        return schedules
    
    def run_scheduled_pipeline(self, schedule_id: str, **kwargs) -> bool:
        """Manually trigger a scheduled pipeline run."""
        if schedule_id not in self.schedules:
            return False
        
        schedule_config = self.schedules[schedule_id]
        return self._execute_pipeline(schedule_config, **kwargs)
    
    def get_next_runs(self, hours: int = 24) -> Dict[str, datetime]:
        """Get next run times for all schedules."""
        cutoff_time = datetime.now() + timedelta(hours=hours)
        next_runs = {}
        
        for schedule_id, schedule_config in self.schedules.items():
            if (schedule_config.enabled and 
                schedule_config.status == ScheduleStatus.ACTIVE and
                schedule_config.next_run and 
                schedule_config.next_run <= cutoff_time):
                next_runs[schedule_id] = schedule_config.next_run
        
        return next_runs
    
    def get_active_jobs(self) -> Dict[str, Dict[str, Any]]:
        """Get currently active jobs."""
        return {
            schedule_id: {
                "schedule": schedule_config.to_dict(),
                "start_time": job_info["start_time"].isoformat(),
                "status": job_info["status"]
            }
            for schedule_id, job_info in self.active_jobs.items()
        }
    
    def _run_scheduler(self):
        """Main scheduler loop."""
        while self.is_running:
            try:
                # Run scheduled jobs
                schedule.run_pending()
                
                # Check for overdue jobs
                self._check_overdue_jobs()
                
                # Update schedule states
                self._update_schedule_states()
                
                time.sleep(1)  # Check every second
                
            except Exception as e:
                self._notify("scheduler_error", {
                    "error": str(e),
                    "timestamp": datetime.now().isoformat()
                })
                time.sleep(5)  # Wait before retrying
    
    def _activate_schedule(self, schedule_config: ScheduleConfig):
        """Activate a schedule."""
        try:
            if schedule_config.schedule_type == ScheduleType.DAILY:
                # Parse time format "HH:MM"
                time_str = schedule_config.expression
                schedule.every().day.at(time_str).do(
                    self._execute_pipeline, schedule_config
                )
                self._calculate_next_run(schedule_config)
                
            elif schedule_config.schedule_type == ScheduleType.WEEKLY:
                # Parse format "DAY HH:MM"
                parts = schedule_config.expression.split()
                if len(parts) == 2:
                    day, time_str = parts
                    day_method = getattr(schedule.every(), day.lower())
                    day_method.at(time_str).do(
                        self._execute_pipeline, schedule_config
                    )
                self._calculate_next_run(schedule_config)
                
            elif schedule_config.schedule_type == ScheduleType.INTERVAL:
                # Parse interval like "30" (minutes)
                interval_minutes = int(schedule_config.expression)
                schedule.every(interval_minutes).minutes.do(
                    self._execute_pipeline, schedule_config
                )
                self._calculate_next_run(schedule_config)
                
            elif schedule_config.schedule_type == ScheduleType.CRON:
                # For cron expressions, we use a simple implementation
                # Note: This is a simplified cron parser
                self._setup_cron_schedule(schedule_config)
                
        except Exception as e:
            self._notify("schedule_activation_error", {
                "schedule_id": schedule_config.schedule_id,
                "error": str(e)
            })
    
    def _deactivate_schedule(self, schedule_config: ScheduleConfig):
        """Deactivate a schedule."""
        # Find and remove the job
        jobs_to_remove = []
        for job in schedule.jobs:
            if hasattr(job, 'tags') and schedule_config.schedule_id in job.tags:
                jobs_to_remove.append(job)
        
        for job in jobs_to_remove:
            schedule.cancel_job(job)
    
    def _setup_cron_schedule(self, schedule_config: ScheduleConfig):
        """Setup cron-based schedule (simplified)."""
        # This is a simplified cron implementation
        # For production, consider using a proper cron library
        cron_parts = schedule_config.expression.split()
        
        if len(cron_parts) != 5:
            raise ValueError("Invalid cron expression")
        
        # For simplicity, we'll just run every 5 minutes if the schedule is enabled
        # A proper implementation would parse the cron expression properly
        schedule.every(5).minutes.do(self._execute_pipeline, schedule_config)
        self._calculate_next_run(schedule_config)
    
    def _execute_pipeline(self, schedule_config: ScheduleConfig, **kwargs) -> bool:
        """Execute a scheduled pipeline."""
        try:
            # Check if schedule should run
            if not self._should_run_schedule(schedule_config):
                return False
            
            # Update run count
            schedule_config.run_count += 1
            schedule_config.last_run = datetime.now()
            schedule_config.status = ScheduleStatus.RUNNING
            
            # Start job tracking
            job_info = {
                "start_time": datetime.now(),
                "status": "running",
                "schedule_config": schedule_config
            }
            self.active_jobs[schedule_config.schedule_id] = job_info
            
            # Save state
            self._save_schedules()
            
            # Execute pipeline in a separate thread
            def run_pipeline():
                try:
                    # Import the pipeline runner (this assumes the runner exists)
                    # You would need to implement this based on your pipeline structure
                    success = self._run_pipeline_process(schedule_config, **kwargs)
                    
                    # Update job status
                    job_info["status"] = "completed" if success else "failed"
                    schedule_config.status = ScheduleStatus.COMPLETED if success else ScheduleStatus.FAILED
                    
                except Exception as e:
                    job_info["status"] = "error"
                    schedule_config.status = ScheduleStatus.FAILED
                    self._notify("pipeline_execution_error", {
                        "schedule_id": schedule_config.schedule_id,
                        "error": str(e)
                    })
                
                finally:
                    # Remove from active jobs
                    if schedule_config.schedule_id in self.active_jobs:
                        del self.active_jobs[schedule_config.schedule_id]
                    
                    # Update next run
                    self._calculate_next_run(schedule_config)
                    self._save_schedules()
            
            pipeline_thread = threading.Thread(target=run_pipeline, daemon=True)
            pipeline_thread.start()
            
            self._notify("pipeline_started", {
                "schedule_id": schedule_config.schedule_id,
                "run_count": schedule_config.run_count
            })
            
            return True
            
        except Exception as e:
            self._notify("pipeline_execution_error", {
                "schedule_id": schedule_config.schedule_id,
                "error": str(e)
            })
            return False
    
    def _run_pipeline_process(self, schedule_config: ScheduleConfig, **kwargs) -> bool:
        """Run the actual pipeline process."""
        # This would integrate with your main pipeline runner
        # For now, we'll create a simple implementation
        
        cmd = ["python", "-m", "pashto_dataset.pipeline.main"]
        if schedule_config.config_path:
            cmd.extend(["--config", schedule_config.config_path])
        
        # Add parameters
        for key, value in schedule_config.parameters.items():
            cmd.extend([f"--{key}", str(value)])
        
        # Add additional kwargs
        for key, value in kwargs.items():
            cmd.extend([f"--{key}", str(value)])
        
        try:
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            stdout, stderr = process.communicate(timeout=3600)  # 1 hour timeout
            return process.returncode == 0
            
        except subprocess.TimeoutExpired:
            process.kill()
            return False
        except Exception:
            return False
    
    def _should_run_schedule(self, schedule_config: ScheduleConfig) -> bool:
        """Check if a schedule should run."""
        if not schedule_config.enabled:
            return False
        
        if schedule_config.status != ScheduleStatus.ACTIVE:
            return False
        
        if (schedule_config.max_runs is not None and 
            schedule_config.run_count >= schedule_config.max_runs):
            return False
        
        if (schedule_config.next_run and 
            datetime.now() < schedule_config.next_run):
            return False
        
        return True
    
    def _calculate_next_run(self, schedule_config: ScheduleConfig):
        """Calculate next run time for a schedule."""
        if schedule_config.schedule_type == ScheduleType.DAILY:
            schedule_config.next_run = self._next_daily_run(schedule_config.expression)
        elif schedule_config.schedule_type == ScheduleType.WEEKLY:
            schedule_config.next_run = self._next_weekly_run(schedule_config.expression)
        elif schedule_config.schedule_type == ScheduleType.INTERVAL:
            schedule_config.next_run = self._next_interval_run(schedule_config.expression)
        elif schedule_config.schedule_type == ScheduleType.CRON:
            schedule_config.next_run = datetime.now() + timedelta(minutes=5)
        else:
            schedule_config.next_run = None
    
    def _next_daily_run(self, time_str: str) -> datetime:
        """Calculate next daily run time."""
        now = datetime.now()
        time_parts = time_str.split(':')
        hour, minute = int(time_parts[0]), int(time_parts[1])
        
        next_run = now.replace(hour=hour, minute=minute, second=0, microsecond=0)
        
        if next_run <= now:
            next_run += timedelta(days=1)
        
        return next_run
    
    def _next_weekly_run(self, expression: str) -> datetime:
        """Calculate next weekly run time."""
        # Simplified implementation - parse "DAY HH:MM"
        parts = expression.split()
        if len(parts) != 2:
            return datetime.now() + timedelta(days=7)
        
        day_name, time_str = parts
        now = datetime.now()
        
        # Get target day of week
        days = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']
        target_day = days.index(day_name.lower())
        current_day = now.weekday()
        
        days_ahead = target_day - current_day
        if days_ahead <= 0:
            days_ahead += 7
        
        next_run = now + timedelta(days=days_ahead)
        
        # Set time
        time_parts = time_str.split(':')
        hour, minute = int(time_parts[0]), int(time_parts[1])
        next_run = next_run.replace(hour=hour, minute=minute, second=0, microsecond=0)
        
        return next_run
    
    def _next_interval_run(self, interval_str: str) -> datetime:
        """Calculate next interval run time."""
        minutes = int(interval_str)
        return datetime.now() + timedelta(minutes=minutes)
    
    def _check_overdue_jobs(self):
        """Check for overdue jobs and handle them."""
        current_time = datetime.now()
        overdue_jobs = []
        
        for schedule_id, job_info in self.active_jobs.items():
            start_time = job_info["start_time"]
            # Consider job overdue if running for more than 2 hours
            if (current_time - start_time).total_seconds() > 7200:
                overdue_jobs.append(schedule_id)
        
        for schedule_id in overdue_jobs:
            self._stop_job(schedule_id, self.active_jobs[schedule_id])
            del self.active_jobs[schedule_id]
    
    def _stop_job(self, schedule_id: str, job_info: Dict[str, Any]):
        """Stop a running job."""
        schedule_config = job_info["schedule_config"]
        schedule_config.status = ScheduleStatus.FAILED
        self._notify("job_stopped", {
            "schedule_id": schedule_id,
            "reason": "overdue"
        })
    
    def _update_schedule_states(self):
        """Update schedule states based on current conditions."""
        for schedule_config in self.schedules.values():
            if (schedule_config.status == ScheduleStatus.RUNNING and
                schedule_config.schedule_id not in self.active_jobs):
                # Job finished but status wasn't updated
                schedule_config.status = ScheduleStatus.ACTIVE
    
    def _save_schedules(self):
        """Save schedules to file."""
        schedules_data = {
            schedule_id: config.to_dict()
            for schedule_id, config in self.schedules.items()
        }
        
        with open(self.schedules_file, 'w', encoding='utf-8') as f:
            json.dump(schedules_data, f, indent=2, default=str)
    
    def _load_schedules(self):
        """Load schedules from file."""
        if not self.schedules_file.exists():
            return
        
        try:
            with open(self.schedules_file, 'r', encoding='utf-8') as f:
                schedules_data = json.load(f)
            
            self.schedules = {}
            for schedule_id, config_data in schedules_data.items():
                self.schedules[schedule_id] = ScheduleConfig.from_dict(config_data)
        
        except Exception:
            self.schedules = {}
    
    def _notify(self, event_type: str, data: Dict[str, Any]):
        """Send notification."""
        notification = {
            "event_type": event_type,
            "data": data,
            "timestamp": datetime.now().isoformat()
        }
        
        # Call registered handlers
        handler = self.notification_handlers.get(event_type)
        if handler:
            try:
                handler(notification)
            except Exception:
                pass  # Ignore handler errors
    
    def _setup_signal_handlers(self):
        """Setup signal handlers for graceful shutdown."""
        def signal_handler(signum, frame):
            self.stop_scheduler()
        
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)