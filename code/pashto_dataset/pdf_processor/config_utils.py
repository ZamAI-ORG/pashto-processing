"""
Configuration and Utility Functions for Pashto PDF Processor

This module provides configuration settings, utility functions, and example usage
for the Pashto PDF processing module.
"""

import os
import json
from typing import Dict, Any, List, Optional
from pathlib import Path
import logging
from dataclasses import dataclass, asdict
from .pashto_utils import PashtoTextUtils


@dataclass
class ProcessingConfig:
    """Configuration class for PDF processing settings."""
    
    # OCR Settings
    ocr_enabled: bool = True
    ocr_languages: str = "eng+pus"
    ocr_dpi: int = 300
    ocr_config: str = "--psm 6 -l eng+pus --oem 3"
    
    # Text Processing Settings
    clean_text: bool = True
    normalize_text: bool = True
    remove_noise: bool = True
    min_word_length: int = 2
    
    # Quality Assessment Settings
    assess_quality: bool = True
    quality_threshold: float = 0.5
    
    # Output Settings
    save_raw_text: bool = True
    save_cleaned_text: bool = True
    save_normalized_text: bool = True
    save_metadata: bool = True
    save_quality_report: bool = True
    output_encoding: str = "utf-8"
    
    # Performance Settings
    max_pages_per_batch: int = 10
    parallel_processing: bool = False
    max_workers: int = 4
    
    # Pashto-specific Settings
    pashto_font_detection: bool = True
    pashto_encoding_priority: List[str] = None
    handle_arabic_similar: bool = True
    
    def __post_init__(self):
        """Initialize default values that depend on other fields."""
        if self.pashto_encoding_priority is None:
            self.pashto_encoding_priority = ["utf-8", "utf-16", "cp1256", "iso-8859-6"]


class ConfigManager:
    """Manages configuration loading, saving, and validation."""
    
    def __init__(self, config_path: str = None):
        """
        Initialize configuration manager.
        
        Args:
            config_path: Path to configuration file
        """
        self.config_path = config_path
        self.pashto_utils = PashtoTextUtils()
        
    def load_config(self, config_path: str = None) -> ProcessingConfig:
        """
        Load configuration from file or create default.
        
        Args:
            config_path: Path to configuration file
            
        Returns:
            ProcessingConfig object
        """
        if config_path is None:
            config_path = self.config_path
        
        if config_path and os.path.exists(config_path):
            try:
                with open(config_path, 'r', encoding='utf-8') as f:
                    config_data = json.load(f)
                return ProcessingConfig(**config_data)
            except Exception as e:
                logging.warning(f"Error loading config: {e}. Using defaults.")
        
        return ProcessingConfig()
    
    def save_config(self, config: ProcessingConfig, config_path: str = None):
        """
        Save configuration to file.
        
        Args:
            config: Configuration object to save
            config_path: Path to save configuration
        """
        if config_path is None:
            config_path = self.config_path
        
        if config_path:
            try:
                config_data = asdict(config)
                with open(config_path, 'w', encoding='utf-8') as f:
                    json.dump(config_data, f, ensure_ascii=False, indent=2)
            except Exception as e:
                logging.error(f"Error saving config: {e}")
    
    def validate_config(self, config: ProcessingConfig) -> List[str]:
        """
        Validate configuration settings.
        
        Args:
            config: Configuration to validate
            
        Returns:
            List of validation errors (empty if valid)
        """
        errors = []
        
        # Validate OCR settings
        if config.ocr_enabled and not config.ocr_languages:
            errors.append("OCR languages must be specified when OCR is enabled")
        
        # Validate DPI settings
        if not 72 <= config.ocr_dpi <= 600:
            errors.append("OCR DPI must be between 72 and 600")
        
        # Validate quality threshold
        if not 0.0 <= config.quality_threshold <= 1.0:
            errors.append("Quality threshold must be between 0.0 and 1.0")
        
        # Validate performance settings
        if config.max_pages_per_batch < 1:
            errors.append("Max pages per batch must be at least 1")
        
        if config.max_workers < 1:
            errors.append("Max workers must be at least 1")
        
        return errors


class PashtoPDFProcessorError(Exception):
    """Custom exception for Pashto PDF processing errors."""
    pass


class FileProcessor:
    """Utility class for file processing operations."""
    
    @staticmethod
    def ensure_directory(path: str) -> str:
        """
        Ensure directory exists, create if not.
        
        Args:
            path: Directory path
            
        Returns:
            The directory path
        """
        Path(path).mkdir(parents=True, exist_ok=True)
        return path
    
    @staticmethod
    def get_file_info(file_path: str) -> Dict[str, Any]:
        """
        Get comprehensive file information.
        
        Args:
            file_path: Path to file
            
        Returns:
            Dictionary with file information
        """
        file_path = Path(file_path)
        
        info = {
            'path': str(file_path.absolute()),
            'name': file_path.name,
            'stem': file_path.stem,
            'suffix': file_path.suffix,
            'size': file_path.stat().st_size if file_path.exists() else 0,
            'created': file_path.stat().st_ctime if file_path.exists() else 0,
            'modified': file_path.stat().st_mtime if file_path.exists() else 0,
            'is_pdf': file_path.suffix.lower() == '.pdf',
            'exists': file_path.exists()
        }
        
        return info
    
    @staticmethod
    def list_pdfs(directory: str, pattern: str = "*.pdf") -> List[str]:
        """
        List all PDF files in a directory.
        
        Args:
            directory: Directory to search
            pattern: File pattern to match
            
        Returns:
            List of PDF file paths
        """
        dir_path = Path(directory)
        pdf_files = list(dir_path.glob(pattern))
        return [str(file) for file in pdf_files if file.suffix.lower() == '.pdf']
    
    @staticmethod
    def backup_file(file_path: str, backup_dir: str = None) -> str:
        """
        Create a backup of a file.
        
        Args:
            file_path: Path to file to backup
            backup_dir: Directory for backup files
            
        Returns:
            Path to backup file
        """
        import shutil
        from datetime import datetime
        
        original_path = Path(file_path)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        if backup_dir is None:
            backup_dir = original_path.parent / "backups"
        
        backup_path = Path(backup_dir) / f"{original_path.stem}_{timestamp}{original_path.suffix}"
        FileProcessor.ensure_directory(str(backup_path.parent))
        
        shutil.copy2(file_path, str(backup_path))
        return str(backup_path)


class PashtoValidationUtils:
    """Utilities for validating Pashto content and quality."""
    
    @staticmethod
    def is_valid_pashto_text(text: str, min_ratio: float = 0.3) -> bool:
        """
        Check if text contains sufficient Pashto content.
        
        Args:
            text: Text to validate
            min_ratio: Minimum ratio of Pashto characters required
            
        Returns:
            True if text is likely Pashto
        """
        if not text:
            return False
        
        pashto_utils = PashtoTextUtils()
        stats = pashto_utils.get_text_statistics(text)
        return stats.get('pashto_ratio', 0) >= min_ratio
    
    @staticmethod
    def validate_pdf_for_pashto(pdf_path: str) -> Dict[str, Any]:
        """
        Validate if PDF is suitable for Pashto processing.
        
        Args:
            pdf_path: Path to PDF file
            
        Returns:
            Validation report
        """
        import fitz
        
        validation = {
            'file_valid': False,
            'readable': False,
            'has_text': False,
            'has_images': False,
            'page_count': 0,
            'estimated_pashto_content': 0.0,
            'recommendations': []
        }
        
        try:
            # Check if file exists and is readable
            if not os.path.exists(pdf_path):
                validation['recommendations'].append("File does not exist")
                return validation
            
            # Open PDF
            doc = fitz.open(pdf_path)
            validation['file_valid'] = True
            validation['readable'] = True
            validation['page_count'] = len(doc)
            
            # Analyze first few pages
            sample_text = ""
            for page_num in range(min(3, len(doc))):
                page = doc.load_page(page_num)
                sample_text += page.get_text()
            
            doc.close()
            
            # Check for text content
            if sample_text.strip():
                validation['has_text'] = True
                validation['estimated_pashto_content'] = PashtoValidationUtils._estimate_pashto_content(sample_text)
            else:
                validation['recommendations'].append("No extractable text found - may need OCR")
            
            # Check for images (potential for OCR)
            validation['has_images'] = PashtoValidationUtils._check_for_images(pdf_path)
            
            # Generate recommendations
            if validation['estimated_pashto_content'] > 0.5:
                validation['recommendations'].append("Good candidate for Pashto processing")
            elif validation['estimated_pashto_content'] > 0.2:
                validation['recommendations'].append("Moderate Pashto content - may need OCR")
            else:
                validation['recommendations'].append("Low Pashto content - verify document type")
            
            if validation['has_images'] and not validation['has_text']:
                validation['recommendations'].append("Image-based PDF - OCR will be required")
            
        except Exception as e:
            validation['error'] = str(e)
            validation['recommendations'].append(f"Error reading PDF: {str(e)}")
        
        return validation
    
    @staticmethod
    def _estimate_pashto_content(text: str) -> float:
        """Estimate Pashto content ratio in text."""
        pashto_utils = PashtoTextUtils()
        stats = pashto_utils.get_text_statistics(text)
        return stats.get('pashto_ratio', 0)
    
    @staticmethod
    def _check_for_images(pdf_path: str) -> bool:
        """Check if PDF contains images."""
        import fitz
        
        try:
            doc = fitz.open(pdf_path)
            for page_num in range(min(3, len(doc))):
                page = doc.load_page(page_num)
                text_dict = page.get_text("dict")
                has_images = any(
                    block.get("type") == 1 for block in text_dict.get("blocks", [])
                )
                if has_images:
                    doc.close()
                    return True
            doc.close()
        except Exception:
            pass
        
        return False


# Example usage and testing functions
def create_sample_config(output_path: str):
    """
    Create a sample configuration file.
    
    Args:
        output_path: Path to save sample configuration
    """
    config = ProcessingConfig()
    config_manager = ConfigManager(output_path)
    config_manager.save_config(config)
    print(f"Sample configuration saved to: {output_path}")


def setup_logging(level: str = "INFO", log_file: str = None):
    """
    Setup logging for the application.
    
    Args:
        level: Logging level
        log_file: Optional log file path
    """
    log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    
    handlers = [logging.StreamHandler()]
    if log_file:
        handlers.append(logging.FileHandler(log_file, encoding='utf-8'))
    
    logging.basicConfig(
        level=getattr(logging, level.upper()),
        format=log_format,
        handlers=handlers
    )


def get_system_info() -> Dict[str, Any]:
    """
    Get system information relevant to Pashto PDF processing.
    
    Returns:
        Dictionary with system information
    """
    import platform
    import sys
    
    info = {
        'platform': platform.platform(),
        'python_version': sys.version,
        'architecture': platform.architecture(),
        'processor': platform.processor(),
    }
    
    # Check for required dependencies
    dependencies = {
        'pymupdf': 'fitz',
        'pytesseract': 'pytesseract',
        'pillow': 'PIL',
        'opencv': 'cv2',
        'numpy': 'numpy'
    }
    
    available_dependencies = {}
    for name, module in dependencies.items():
        try:
            __import__(module)
            available_dependencies[name] = 'available'
        except ImportError:
            available_dependencies[name] = 'missing'
    
    info['dependencies'] = available_dependencies
    
    # Check Tesseract availability
    try:
        import pytesseract
        tesseract_info = pytesseract.get_tesseract_info()
        info['tesseract'] = tesseract_info
    except Exception as e:
        info['tesseract'] = {'error': str(e)}
    
    return info


def example_usage():
    """Example of how to use the Pashto PDF processor."""
    from .pdf_processor import PashtoPDFProcessor
    
    # Example configuration
    config = ProcessingConfig(
        ocr_enabled=True,
        ocr_languages="eng+pus",
        assess_quality=True,
        output_encoding="utf-8"
    )
    
    # Initialize processor
    processor = PashtoPDFProcessor(
        ocr_enabled=config.ocr_enabled,
        ocr_languages=config.ocr_languages
    )
    
    # Example usage
    print("Example Pashto PDF Processing Usage:")
    print("1. Single file processing:")
    print("   result = processor.process_pdf('document.pdf', 'output_dir/')")
    print()
    print("2. Batch processing:")
    print("   results = processor.batch_process('pdfs_dir/', 'output_dir/')")
    print()
    print("3. Configuration:")
    print("   config = ProcessingConfig(ocr_enabled=True, quality_threshold=0.7)")


if __name__ == "__main__":
    # Create sample configuration
    create_sample_config("pashto_processor_config.json")
    print("Sample configuration created.")
    
    # Show system info
    print("\nSystem Information:")
    system_info = get_system_info()
    for key, value in system_info.items():
        print(f"{key}: {value}")
    
    # Show example usage
    print("\nExample Usage:")
    example_usage()