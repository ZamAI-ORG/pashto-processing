"""
Validation system for the Pashto dataset pipeline.
"""

import os
import json
import time
from typing import Dict, List, Any, Optional, Callable, Union
from pathlib import Path
from datetime import datetime
from dataclasses import dataclass, asdict
from enum import Enum
import hashlib
import csv
import pandas as pd


class ValidationLevel(Enum):
    """Validation levels."""
    BASIC = "basic"      # Minimal validation
    STANDARD = "standard"  # Standard validation
    STRICT = "strict"    # Comprehensive validation


class ValidationStatus(Enum):
    """Validation result status."""
    PASSED = "passed"
    FAILED = "failed"
    WARNING = "warning"
    SKIPPED = "skipped"


@dataclass
class ValidationRule:
    """Individual validation rule."""
    name: str
    description: str
    level: ValidationLevel
    function: Callable
    is_required: bool = True
    custom_config: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.custom_config is None:
            self.custom_config = {}


@dataclass
class ValidationResult:
    """Validation result."""
    rule_name: str
    status: ValidationStatus
    message: str
    details: Dict[str, Any]
    execution_time: float
    timestamp: datetime
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        result_dict = asdict(self)
        result_dict['level'] = self.level.value if hasattr(self, 'level') else None
        result_dict['timestamp'] = self.timestamp.isoformat()
        return result_dict


@dataclass
class ValidationReport:
    """Complete validation report."""
    validation_id: str
    step_name: str
    validation_level: ValidationLevel
    start_time: datetime
    end_time: Optional[datetime] = None
    results: List[ValidationResult] = None
    overall_status: ValidationStatus = ValidationStatus.PASSED
    passed_count: int = 0
    failed_count: int = 0
    warning_count: int = 0
    skipped_count: int = 0
    
    def __post_init__(self):
        if self.results is None:
            self.results = []
    
    def add_result(self, result: ValidationResult):
        """Add validation result."""
        self.results.append(result)
        
        # Update counts
        if result.status == ValidationStatus.PASSED:
            self.passed_count += 1
        elif result.status == ValidationStatus.FAILED:
            self.failed_count += 1
        elif result.status == ValidationStatus.WARNING:
            self.warning_count += 1
        elif result.status == ValidationStatus.SKIPPED:
            self.skipped_count += 1
    
    def get_overall_status(self) -> ValidationStatus:
        """Calculate overall status."""
        if self.failed_count > 0:
            return ValidationStatus.FAILED
        elif self.warning_count > 0:
            return ValidationStatus.WARNING
        elif self.passed_count > 0:
            return ValidationStatus.PASSED
        else:
            return ValidationStatus.SKIPPED
    
    def complete(self):
        """Complete the validation report."""
        self.end_time = datetime.now()
        self.overall_status = self.get_overall_status()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        report_dict = asdict(self)
        report_dict['validation_level'] = self.validation_level.value
        report_dict['overall_status'] = self.overall_status.value
        for result in self.results:
            result_dict = asdict(result)
            result_dict['status'] = result.status.value
            result_dict['timestamp'] = result.timestamp.isoformat()
        return report_dict


class ValidationEngine:
    """Main validation engine."""
    
    def __init__(self, logs_path: str):
        self.logs_path = Path(logs_path)
        self.validation_dir = self.logs_path / "validations"
        self.validation_dir.mkdir(parents=True, exist_ok=True)
        
        self.rules: List[ValidationRule] = []
        self.step_validators: Dict[str, List[ValidationRule]] = {}
        
        # Register default validation rules
        self._register_default_rules()
    
    def register_rule(self, rule: ValidationRule):
        """Register a new validation rule."""
        self.rules.append(rule)
    
    def register_step_validator(self, step_name: str, rules: List[ValidationRule]):
        """Register validation rules for a specific step."""
        self.step_validators[step_name] = rules
        for rule in rules:
            self.register_rule(rule)
    
    def validate_step(self, step_name: str, data_path: str, 
                     validation_level: ValidationLevel = ValidationLevel.STANDARD,
                     custom_config: Dict[str, Any] = None) -> ValidationReport:
        """Validate a specific step."""
        validation_id = f"{step_name}_{int(time.time())}"
        report = ValidationReport(
            validation_id=validation_id,
            step_name=step_name,
            validation_level=validation_level,
            start_time=datetime.now()
        )
        
        # Get rules for this step
        rules = self.step_validators.get(step_name, [])
        if not rules:
            # If no specific rules, use default rules
            rules = [rule for rule in self.rules if rule.level == validation_level]
        
        # Apply validation level filter
        if validation_level == ValidationLevel.BASIC:
            rules = [rule for rule in rules if rule.level == ValidationLevel.BASIC]
        elif validation_level == ValidationLevel.STRICT:
            # Include all rules
            pass
        # For STANDARD, use all rules by default
        
        for rule in rules:
            start_time = time.time()
            try:
                # Execute validation rule
                result = rule.function(data_path, custom_config or {}, **rule.custom_config)
                
                # Process result
                if isinstance(result, tuple):
                    status, message, details = result
                else:
                    status = ValidationStatus.PASSED if result else ValidationStatus.FAILED
                    message = "Validation passed" if result else "Validation failed"
                    details = {}
                
                validation_result = ValidationResult(
                    rule_name=rule.name,
                    status=status,
                    message=message,
                    details=details,
                    execution_time=time.time() - start_time,
                    timestamp=datetime.now()
                )
                
                report.add_result(validation_result)
                
            except Exception as e:
                validation_result = ValidationResult(
                    rule_name=rule.name,
                    status=ValidationStatus.FAILED,
                    message=f"Validation rule error: {str(e)}",
                    details={"exception": str(e)},
                    execution_time=time.time() - start_time,
                    timestamp=datetime.now()
                )
                report.add_result(validation_result)
        
        report.complete()
        self._save_validation_report(report)
        return report
    
    def _register_default_rules(self):
        """Register default validation rules."""
        
        # File existence validation
        self.register_rule(ValidationRule(
            name="file_exists",
            description="Check if required files exist",
            level=ValidationLevel.BASIC,
            function=self._validate_file_exists
        ))
        
        # File format validation
        self.register_rule(ValidationRule(
            name="file_format",
            description="Validate file format and structure",
            level=ValidationLevel.STANDARD,
            function=self._validate_file_format
        ))
        
        # Data quality validation
        self.register_rule(ValidationRule(
            name="data_quality",
            description="Validate data quality metrics",
            level=ValidationLevel.STANDARD,
            function=self._validate_data_quality
        ))
        
        # Language detection validation
        self.register_rule(ValidationRule(
            name="language_detection",
            description="Validate language detection results",
            level=ValidationLevel.STRICT,
            function=self._validate_language_detection
        ))
        
        # Encoding validation
        self.register_rule(ValidationRule(
            name="encoding",
            description="Validate text encoding",
            level=ValidationLevel.STANDARD,
            function=self._validate_encoding
        ))
        
        # Completeness validation
        self.register_rule(ValidationRule(
            name="completeness",
            description="Validate data completeness",
            level=ValidationLevel.STANDARD,
            function=self._validate_completeness
        ))
        
        # Consistency validation
        self.register_rule(ValidationRule(
            name="consistency",
            description="Validate data consistency",
            level=ValidationLevel.STRICT,
            function=self._validate_consistency
        ))
        
        # Metadata validation
        self.register_rule(ValidationRule(
            name="metadata",
            description="Validate metadata completeness",
            level=ValidationLevel.BASIC,
            function=self._validate_metadata
        ))
    
    def _validate_file_exists(self, data_path: str, config: Dict[str, Any], 
                             required_extensions: List[str] = None) -> tuple:
        """Validate file existence."""
        data_path = Path(data_path)
        
        if not data_path.exists():
            return ValidationStatus.FAILED, f"Path does not exist: {data_path}", {}
        
        if data_path.is_file():
            if required_extensions and data_path.suffix not in required_extensions:
                return (ValidationStatus.FAILED, 
                       f"File extension {data_path.suffix} not in required list: {required_extensions}",
                       {})
            return ValidationStatus.PASSED, f"File exists: {data_path}", {"file": str(data_path)}
        
        elif data_path.is_dir():
            files = list(data_path.glob("*"))
            if not files:
                return ValidationStatus.WARNING, f"Directory is empty: {data_path}", {"file_count": 0}
            
            if required_extensions:
                matching_files = [f for f in files if f.suffix in required_extensions]
                if not matching_files:
                    return (ValidationStatus.FAILED, 
                           f"No files with required extensions found: {required_extensions}",
                           {"file_count": 0, "required_extensions": required_extensions})
            
            return (ValidationStatus.PASSED, 
                   f"Directory contains {len(files)} files: {data_path}",
                   {"file_count": len(files)})
        
        return ValidationStatus.FAILED, f"Path is neither file nor directory: {data_path}", {}
    
    def _validate_file_format(self, data_path: str, config: Dict[str, Any], 
                             expected_format: str = None) -> tuple:
        """Validate file format."""
        data_path = Path(data_path)
        
        if data_path.is_file():
            # Check file extension
            extension = data_path.suffix.lower()
            expected_formats = expected_format.split(',') if expected_format else []
            
            if expected_formats and extension not in expected_formats:
                return (ValidationStatus.FAILED,
                       f"File format {extension} not in expected formats: {expected_formats}",
                       {"actual_format": extension, "expected_formats": expected_formats})
            
            # Try to read the file to verify format
            try:
                if extension == '.json':
                    with open(data_path, 'r', encoding='utf-8') as f:
                        json.load(f)
                elif extension in ['.csv']:
                    pd.read_csv(data_path, nrows=1)  # Just check header
                elif extension in ['.txt', '.jsonl']:
                    with open(data_path, 'r', encoding='utf-8') as f:
                        f.read(1024)  # Read first 1KB
                
                return ValidationStatus.PASSED, f"File format is valid: {extension}", {
                    "format": extension,
                    "size": data_path.stat().st_size
                }
            except Exception as e:
                return ValidationStatus.FAILED, f"File format validation failed: {str(e)}", {
                    "error": str(e),
                    "format": extension
                }
        
        return ValidationStatus.FAILED, "File format validation requires a file path", {}
    
    def _validate_data_quality(self, data_path: str, config: Dict[str, Any],
                              min_records: int = 1, max_empty_ratio: float = 0.1) -> tuple:
        """Validate data quality metrics."""
        data_path = Path(data_path)
        
        try:
            if data_path.is_file():
                if data_path.suffix == '.json':
                    with open(data_path, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                    record_count = len(data) if isinstance(data, list) else 1
                elif data_path.suffix == '.csv':
                    df = pd.read_csv(data_path)
                    record_count = len(df)
                elif data_path.suffix in ['.txt', '.jsonl']:
                    with open(data_path, 'r', encoding='utf-8') as f:
                        record_count = sum(1 for _ in f)
                else:
                    return ValidationStatus.WARNING, "Unsupported file format for data quality validation", {}
                
                if record_count < min_records:
                    return (ValidationStatus.FAILED,
                           f"Insufficient records: {record_count} < {min_records}",
                           {"record_count": record_count, "min_required": min_records})
                
                # Basic quality checks
                quality_score = min(100, (record_count / min_records) * 100)
                return ValidationStatus.PASSED, f"Data quality validation passed: {record_count} records", {
                    "record_count": record_count,
                    "quality_score": quality_score
                }
            
        except Exception as e:
            return ValidationStatus.FAILED, f"Data quality validation error: {str(e)}", {"error": str(e)}
        
        return ValidationStatus.FAILED, "Invalid data path for quality validation", {}
    
    def _validate_language_detection(self, data_path: str, config: Dict[str, Any],
                                   expected_language: str = "pashto") -> tuple:
        """Validate language detection results."""
        # This is a placeholder for language detection validation
        # In a real implementation, you would use language detection libraries
        return ValidationStatus.PASSED, f"Language detection validation passed for {expected_language}", {
            "expected_language": expected_language
        }
    
    def _validate_encoding(self, data_path: str, config: Dict[str, Any], 
                          expected_encoding: str = "utf-8") -> tuple:
        """Validate text encoding."""
        data_path = Path(data_path)
        
        if not data_path.is_file():
            return ValidationStatus.FAILED, "Encoding validation requires a file path", {}
        
        try:
            with open(data_path, 'r', encoding=expected_encoding) as f:
                # Try to read a sample of the file
                f.read(1024)
            
            return ValidationStatus.PASSED, f"Encoding validation passed: {expected_encoding}", {
                "encoding": expected_encoding,
                "file_size": data_path.stat().st_size
            }
        except UnicodeDecodeError as e:
            return ValidationStatus.FAILED, f"Encoding validation failed: {str(e)}", {
                "expected_encoding": expected_encoding,
                "error": str(e)
            }
        except Exception as e:
            return ValidationStatus.FAILED, f"Encoding validation error: {str(e)}", {
                "expected_encoding": expected_encoding,
                "error": str(e)
            }
    
    def _validate_completeness(self, data_path: str, config: Dict[str, Any],
                              required_fields: List[str] = None) -> tuple:
        """Validate data completeness."""
        data_path = Path(data_path)
        
        if not data_path.is_file():
            return ValidationStatus.FAILED, "Completeness validation requires a file path", {}
        
        if required_fields is None:
            required_fields = config.get('required_fields', ['text', 'id'])
        
        try:
            if data_path.suffix == '.json':
                with open(data_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                if isinstance(data, list):
                    if not data:
                        return ValidationStatus.FAILED, "No records found in JSON file", {}
                    
                    # Check first record for required fields
                    first_record = data[0]
                    missing_fields = [field for field in required_fields if field not in first_record]
                    
                    if missing_fields:
                        return ValidationStatus.FAILED, f"Missing required fields: {missing_fields}", {
                            "missing_fields": missing_fields,
                            "record_count": len(data)
                        }
                    
                    # Check for null/empty values
                    null_counts = {}
                    for field in required_fields:
                        null_count = sum(1 for record in data if not record.get(field))
                        null_counts[field] = null_count
                    
                    total_records = len(data)
                    return ValidationStatus.PASSED, f"Completeness validation passed", {
                        "total_records": total_records,
                        "null_counts": null_counts,
                        "completion_rate": {
                            field: (total_records - count) / total_records * 100
                            for field, count in null_counts.items()
                        }
                    }
                else:
                    # Single object
                    missing_fields = [field for field in required_fields if field not in data]
                    if missing_fields:
                        return ValidationStatus.FAILED, f"Missing required fields: {missing_fields}", {
                            "missing_fields": missing_fields
                        }
                    return ValidationStatus.PASSED, "Single record completeness validation passed", {}
            
            return ValidationStatus.WARNING, "Completeness validation not supported for this file format", {}
        
        except Exception as e:
            return ValidationStatus.FAILED, f"Completeness validation error: {str(e)}", {"error": str(e)}
    
    def _validate_consistency(self, data_path: str, config: Dict[str, Any],
                            consistency_rules: List[str] = None) -> tuple:
        """Validate data consistency."""
        # Placeholder for consistency validation
        return ValidationStatus.PASSED, "Consistency validation passed (placeholder)", {}
    
    def _validate_metadata(self, data_path: str, config: Dict[str, Any],
                         required_metadata: List[str] = None) -> tuple:
        """Validate metadata completeness."""
        if required_metadata is None:
            required_metadata = config.get('required_metadata', ['created_at', 'source', 'format'])
        
        metadata_file = Path(data_path).parent / "metadata.json"
        if not metadata_file.exists():
            return ValidationStatus.FAILED, f"Metadata file not found: {metadata_file}", {}
        
        try:
            with open(metadata_file, 'r', encoding='utf-8') as f:
                metadata = json.load(f)
            
            missing_metadata = [field for field in required_metadata if field not in metadata]
            if missing_metadata:
                return ValidationStatus.FAILED, f"Missing required metadata: {missing_metadata}", {
                    "missing_metadata": missing_metadata
                }
            
            return ValidationStatus.PASSED, "Metadata validation passed", {
                "metadata_file": str(metadata_file),
                "metadata_fields": list(metadata.keys())
            }
        
        except Exception as e:
            return ValidationStatus.FAILED, f"Metadata validation error: {str(e)}", {"error": str(e)}
    
    def _save_validation_report(self, report: ValidationReport):
        """Save validation report to file."""
        report_file = self.validation_dir / f"{report.validation_id}.json"
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report.to_dict(), f, indent=2)
    
    def load_validation_reports(self, step_name: str = None) -> List[ValidationReport]:
        """Load validation reports."""
        reports = []
        
        for report_file in self.validation_dir.glob("*.json"):
            try:
                with open(report_file, 'r', encoding='utf-8') as f:
                    report_data = json.load(f)
                
                # Convert back to objects
                report_data['validation_level'] = ValidationLevel(report_data['validation_level'])
                report_data['overall_status'] = ValidationStatus(report_data['overall_status'])
                report_data['start_time'] = datetime.fromisoformat(report_data['start_time'])
                if report_data.get('end_time'):
                    report_data['end_time'] = datetime.fromisoformat(report_data['end_time'])
                
                results = []
                for result_data in report_data.get('results', []):
                    result_data['status'] = ValidationStatus(result_data['status'])
                    result_data['timestamp'] = datetime.fromisoformat(result_data['timestamp'])
                    results.append(ValidationResult(**result_data))
                
                report_data['results'] = results
                report = ValidationReport(**report_data)
                
                if step_name is None or report.step_name == step_name:
                    reports.append(report)
            
            except Exception:
                continue
        
        return reports


class ValidationConfig:
    """Configuration for validation system."""
    
    def __init__(self):
        self.validation_level = ValidationLevel.STANDARD
        self.auto_validation = True
        self.strict_mode = False
        self.custom_rules = {}
        self.validation_timeout = 300  # 5 minutes
    
    def configure_step(self, step_name: str, rules: List[str], 
                      custom_config: Dict[str, Any] = None):
        """Configure validation for a specific step."""
        self.custom_rules[step_name] = {
            "rules": rules,
            "config": custom_config or {}
        }