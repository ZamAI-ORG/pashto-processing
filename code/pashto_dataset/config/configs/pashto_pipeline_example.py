#!/usr/bin/env python3
"""
Pashto Dataset Pipeline - Configuration Usage Example

This script demonstrates how to use the Pashto dataset configurations
for text collection, processing, and quality assessment.
"""

import json
import logging
import os
import sys
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from datetime import datetime

# Add the current directory to Python path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from langdetect import detect, DetectorFactory
    from langdetect.lang_detect_exception import LangDetectException
    import unicodedata
    import re
    from bs4 import BeautifulSoup
    import requests
    from requests.adapters import HTTPAdapter
    from urllib3.util.retry import Retry
except ImportError as e:
    print(f"Warning: Some dependencies not available: {e}")
    print("Please install: langdetect, beautifulsoup4, requests, unicodedata")

# Set language detection seed for consistent results
DetectorFactory.seed = 0

@dataclass
class ProcessingResult:
    """Data class for processing results"""
    content: str
    language: str
    quality_score: float
    word_count: int
    char_count: int
    metadata: Dict[str, Any]
    source: str
    processing_date: str

class PashtoConfigManager:
    """Manages Pashto dataset configurations"""
    
    def __init__(self, config_dir: str = "configs"):
        self.config_dir = Path(config_dir)
        self.configs = self._load_all_configs()
        
    def _load_all_configs(self) -> Dict[str, Any]:
        """Load all configuration files"""
        configs = {}
        config_files = {
            "main": "main_config.json",
            "sources": "source_config.json", 
            "scraping": "scraping_config.json",
            "processing": "processing_config.json"
        }
        
        for key, filename in config_files.items():
            config_path = self.config_dir / filename
            try:
                with open(config_path, 'r', encoding='utf-8') as f:
                    configs[key] = json.load(f)
                print(f"✓ Loaded {key} config: {config_path}")
            except FileNotFoundError:
                print(f"✗ Config file not found: {config_path}")
                configs[key] = {}
            except json.JSONDecodeError as e:
                print(f"✗ JSON error in {config_path}: {e}")
                configs[key] = {}
                
        return configs
    
    def get(self, config_type: str, key: str = None, default: Any = None) -> Any:
        """Get configuration value"""
        config = self.configs.get(config_type, {})
        if key:
            return config.get(key, default)
        return config

class PashtoTextProcessor:
    """Core Pashto text processing class"""
    
    def __init__(self, config_manager: PashtoConfigManager):
        self.config_manager = config_manager
        self.setup_logging()
        
        # Load Pashto-specific patterns
        self.pashto_ranges = [
            (0x0600, 0x06FF),    # Arabic
            (0x0750, 0x077F),    # Arabic Supplement
            (0xFB50, 0xFDFF),    # Arabic Presentation Forms-A
            (0xFE70, 0xFEFF)     # Arabic Presentation Forms-B
        ]
        
    def setup_logging(self):
        """Setup logging configuration"""
        log_config = self.config_manager.get("main", "global_settings", {}).get("logging", {})
        logging.basicConfig(
            level=getattr(logging, log_config.get("level", "INFO")),
            format=log_config.get("format", "%(asctime)s - %(name)s - %(levelname)s - %(message)s"),
            handlers=[
                logging.FileHandler(log_config.get("file", "pashto_dataset.log"), encoding='utf-8'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
    
    def normalize_unicode(self, text: str) -> str:
        """Normalize Unicode text"""
        normalization_config = self.config_manager.get("processing", "text_processing", {}).get("encoding_handling", {}).get("unicode_normalization", {})
        
        try:
            # Normalize Unicode
            text = unicodedata.normalize(
                normalization_config.get("form", "NFC"), 
                text
            )
            
            # Remove zero-width characters if configured
            if normalization_config.get("remove_zero_width", True):
                text = ''.join(char for char in text if unicodedata.category(char) != 'Cf')
                
            # Normalize Arabic shapes
            if normalization_config.get("normalize_arabic_shapes", True):
                text = self._normalize_arabic_shapes(text)
                
            return text
            
        except Exception as e:
            self.logger.error(f"Unicode normalization failed: {e}")
            return text
    
    def _normalize_arabic_shapes(self, text: str) -> str:
        """Normalize Arabic character shapes"""
        # Simple shape normalization - in production, use python-arabic-reshaper
        normalization_map = {
            # Add specific Pashto character normalizations here
            'ي': 'ی',  # Arabic yeh to Persian yeh
        }
        
        for arabic, persian in normalization_map.items():
            text = text.replace(arabic, persian)
            
        return text
    
    def detect_language(self, text: str) -> Dict[str, Any]:
        """Detect language with confidence score"""
        lang_config = self.config_manager.get("processing", "language_processing", {}).get("detection", {})
        confidence_threshold = lang_config.get("confidence_threshold", 0.7)
        
        result = {
            "language": "unknown",
            "confidence": 0.0,
            "method": "none"
        }
        
        try:
            # Try langdetect
            if 'langdetect' in sys.modules:
                detected_lang = detect(text)
                result["language"] = detected_lang
                result["method"] = "langdetect"
                
                # For Pashto, try additional validation
                if detected_lang.lower() in ['ps', 'fa', 'ur']:
                    pashto_score = self._validate_pashto_script(text)
                    if pashto_score > 0.6:
                        result["language"] = "ps"
                        result["confidence"] = pashto_score
                    else:
                        result["confidence"] = 0.3
                else:
                    result["confidence"] = 0.5
                    
        except LangDetectException as e:
            self.logger.warning(f"Language detection failed: {e}")
            # Fallback to character analysis
            result.update(self._fallback_language_detection(text))
            
        return result
    
    def _validate_pashto_script(self, text: str) -> float:
        """Validate if text contains Pashto script"""
        if not text:
            return 0.0
            
        pashto_chars = 0
        total_chars = 0
        
        for char in text:
            if char.strip():  # Skip whitespace
                total_chars += 1
                for start, end in self.pashto_ranges:
                    if start <= ord(char) <= end:
                        pashto_chars += 1
                        break
                        
        return pashto_chars / total_chars if total_chars > 0 else 0.0
    
    def _fallback_language_detection(self, text: str) -> Dict[str, Any]:
        """Fallback language detection using character analysis"""
        pashto_score = self._validate_pashto_script(text)
        
        if pashto_score > 0.6:
            return {"language": "ps", "confidence": pashto_score, "method": "char_analysis"}
        else:
            return {"language": "unknown", "confidence": 0.0, "method": "char_analysis"}
    
    def assess_quality(self, text: str) -> Dict[str, float]:
        """Assess text quality using various metrics"""
        quality_config = self.config_manager.get("processing", "quality_assessment", {}).get("content_quality", {})
        
        metrics = {}
        
        # Length metrics
        char_count = len(text)
        word_count = len(text.split())
        
        metrics["char_count"] = char_count
        metrics["word_count"] = word_count
        
        # Pashto character ratio
        metrics["pashto_char_ratio"] = self._validate_pashto_script(text)
        
        # Encoding validity (simplified)
        metrics["encoding_validity"] = 1.0 if self._is_valid_encoding(text) else 0.0
        
        # Calculate overall quality score
        quality_thresholds = quality_config.get("technical_metrics", {})
        
        quality_score = 0.0
        quality_score += min(metrics.get("pashto_char_ratio", 0) * 0.4, 0.4)
        quality_score += min(metrics.get("encoding_validity", 0) * 0.3, 0.3)
        
        # Length penalty/bonus
        if 100 <= char_count <= 5000:
            quality_score += 0.3
        elif char_count < 50 or char_count > 50000:
            quality_score -= 0.2
            
        metrics["quality_score"] = max(0.0, min(1.0, quality_score))
        
        return metrics
    
    def _is_valid_encoding(self, text: str) -> bool:
        """Check if text has valid encoding"""
        try:
            text.encode('utf-8').decode('utf-8')
            return True
        except UnicodeError:
            return False
    
    def extract_text_from_html(self, html_content: str) -> str:
        """Extract clean text from HTML content"""
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # Remove script and style elements
            for script in soup(["script", "style", "nav", "footer"]):
                script.decompose()
                
            # Get text and clean it
            text = soup.get_text()
            
            # Clean up whitespace
            lines = (line.strip() for line in text.splitlines())
            chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
            text = ' '.join(chunk for chunk in chunks if chunk)
            
            return text
            
        except Exception as e:
            self.logger.error(f"HTML extraction failed: {e}")
            return ""
    
    def process_text(self, content: str, source: str = "unknown") -> ProcessingResult:
        """Main text processing pipeline"""
        self.logger.info(f"Processing text from {source} (length: {len(content)})")
        
        try:
            # Step 1: Normalize Unicode
            content = self.normalize_unicode(content)
            
            # Step 2: Detect language
            lang_result = self.detect_language(content)
            
            # Step 3: Assess quality
            quality_metrics = self.assess_quality(content)
            
            # Step 4: Create result
            result = ProcessingResult(
                content=content,
                language=lang_result["language"],
                quality_score=quality_metrics["quality_score"],
                word_count=quality_metrics["word_count"],
                char_count=quality_metrics["char_count"],
                metadata={
                    "language_confidence": lang_result["confidence"],
                    "language_method": lang_result["method"],
                    "pashto_char_ratio": quality_metrics["pashto_char_ratio"],
                    "encoding_validity": quality_metrics["encoding_validity"]
                },
                source=source,
                processing_date=datetime.now().isoformat()
            )
            
            self.logger.info(f"Processing complete: {result.language}, quality: {result.quality_score:.2f}")
            return result
            
        except Exception as e:
            self.logger.error(f"Processing failed: {e}")
            raise

class PashtoDatasetPipeline:
    """Main dataset pipeline orchestrator"""
    
    def __init__(self, config_dir: str = "configs"):
        self.config_manager = PashtoConfigManager(config_dir)
        self.processor = PashtoTextProcessor(self.config_manager)
        self.results: List[ProcessingResult] = []
        
    def add_sample_text(self, text: str, source: str = "sample"):
        """Add sample text for processing"""
        result = self.processor.process_text(text, source)
        
        # Apply quality filters
        quality_threshold = self.config_manager.get("main", "global_settings", {}).get("text_processing", {}).get("quality_threshold", 0.6)
        
        if result.quality_score >= quality_threshold and result.language == "ps":
            self.results.append(result)
            return True
        else:
            print(f"Text filtered out: quality={result.quality_score:.2f}, lang={result.language}")
            return False
    
    def save_results(self, output_dir: str = "output", formats: List[str] = None):
        """Save processed results to files"""
        if not formats:
            formats = self.config_manager.get("main", "global_settings", {}).get("output", {}).get("formats", ["json"])
            
        output_path = Path(output_dir)
        output_path.mkdir(exist_ok=True)
        
        for fmt in formats:
            if fmt == "json":
                self._save_json(output_path)
            elif fmt == "csv":
                self._save_csv(output_path)
            elif fmt == "txt":
                self._save_txt(output_path)
                
        self.logger.info(f"Saved {len(self.results)} results to {output_path}")
    
    def _save_json(self, output_path: Path):
        """Save results as JSON"""
        data = {
            "metadata": {
                "total_documents": len(self.results),
                "processing_date": datetime.now().isoformat(),
                "config_version": "1.0.0"
            },
            "documents": [
                {
                    "content": result.content,
                    "language": result.language,
                    "quality_score": result.quality_score,
                    "word_count": result.word_count,
                    "char_count": result.char_count,
                    "metadata": result.metadata,
                    "source": result.source,
                    "processing_date": result.processing_date
                }
                for result in self.results
            ]
        }
        
        with open(output_path / "pashto_dataset.json", 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    
    def _save_csv(self, output_path: Path):
        """Save results as CSV"""
        import csv
        
        with open(output_path / "pashto_dataset.csv", 'w', newline='', encoding='utf-8-sig') as f:
            writer = csv.writer(f)
            writer.writerow(['content', 'language', 'quality_score', 'word_count', 'char_count', 'source', 'processing_date'])
            
            for result in self.results:
                writer.writerow([
                    result.content,
                    result.language,
                    result.quality_score,
                    result.word_count,
                    result.char_count,
                    result.source,
                    result.processing_date
                ])
    
    def _save_txt(self, output_path: Path):
        """Save results as plain text"""
        with open(output_path / "pashto_dataset.txt", 'w', encoding='utf-8') as f:
            for result in self.results:
                f.write(f"=== Document from {result.source} ===\n")
                f.write(f"Language: {result.language}\n")
                f.write(f"Quality Score: {result.quality_score:.2f}\n")
                f.write(f"Word Count: {result.word_count}\n")
                f.write(f"Content:\n{result.content}\n\n")

def main():
    """Main demonstration function"""
    print("Pashto Dataset Pipeline - Configuration Usage Example")
    print("=" * 60)
    
    # Initialize pipeline
    pipeline = PashtoDatasetPipeline()
    
    # Sample Pashto texts for testing
    sample_texts = [
        {
            "text": "پښتو د پښتنو ژبه ده چې د افغانستان او پاکستان په ځینو سیمو کې ویل کېږي.",
            "source": "basic_sample"
        },
        {
            "text": "د سولې د تاسیسولو لپاره، زموږ ټولو ته اړتیا ده چې د ټولنې د ښه والي په خاطر خپل ځانونه قرباني کړو.",
            "source": "literary_sample"
        },
        {
            "text": "Hello world, this is mixed content with English words mixed in Pashto text.",
            "source": "mixed_content"
        }
    ]
    
    print(f"Processing {len(sample_texts)} sample texts...")
    
    # Process sample texts
    for i, sample in enumerate(sample_texts, 1):
        print(f"\n--- Sample {i} ---")
        success = pipeline.add_sample_text(sample["text"], sample["source"])
        print(f"Added: {success}")
    
    # Display processing results
    print(f"\n--- Processing Results ---")
    for result in pipeline.results:
        print(f"Source: {result.source}")
        print(f"Language: {result.language}")
        print(f"Quality: {result.quality_score:.2f}")
        print(f"Words: {result.word_count}")
        print(f"Content preview: {result.content[:50]}...")
        print()
    
    # Save results
    print("Saving results...")
    pipeline.save_results()
    print("Pipeline demonstration complete!")

if __name__ == "__main__":
    main()