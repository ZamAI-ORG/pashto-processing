#!/usr/bin/env python3
"""
Pashto Dataset Pipeline - Configuration Validation Test

This script validates the configuration files and demonstrates basic functionality.
"""

import json
import os
import sys
import unittest
from pathlib import Path

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

class TestPashtoConfig(unittest.TestCase):
    """Test cases for Pashto configuration validation"""
    
    def setUp(self):
        """Set up test environment"""
        self.config_dir = Path(__file__).parent
        self.configs_dir = self.config_dir / "configs"
        
    def test_config_files_exist(self):
        """Test that all required config files exist"""
        required_files = [
            "main_config.json",
            "source_config.json", 
            "scraping_config.json",
            "processing_config.json"
        ]
        
        for filename in required_files:
            config_path = self.configs_dir / filename
            self.assertTrue(config_path.exists(), f"Config file missing: {filename}")
            
    def test_config_files_valid_json(self):
        """Test that all config files contain valid JSON"""
        config_files = [
            "main_config.json",
            "source_config.json",
            "scraping_config.json", 
            "processing_config.json"
        ]
        
        for filename in config_files:
            config_path = self.configs_dir / filename
            try:
                with open(config_path, 'r', encoding='utf-8') as f:
                    json.load(f)
            except json.JSONDecodeError as e:
                self.fail(f"Invalid JSON in {filename}: {e}")
            except FileNotFoundError:
                self.fail(f"Config file not found: {filename}")
                
    def test_main_config_structure(self):
        """Test main configuration has required structure"""
        with open(self.configs_dir / "main_config.json", 'r', encoding='utf-8') as f:
            config = json.load(f)
            
        # Check required top-level keys
        required_keys = ["project", "global_settings", "preprocessing", "quality_control", "data_storage"]
        for key in required_keys:
            self.assertIn(key, config, f"Missing required key: {key}")
            
        # Check global settings
        global_settings = config["global_settings"]
        self.assertIn("encoding", global_settings)
        self.assertIn("text_processing", global_settings)
        
    def test_source_config_structure(self):
        """Test source configuration has required structure"""
        with open(self.configs_dir / "source_config.json", 'r', encoding='utf-8') as f:
            config = json.load(f)
            
        # Check sources exist
        self.assertIn("sources", config)
        sources = config["sources"]
        
        # Check expected source categories
        expected_categories = ["digital_libraries", "academic_datasets", "newspapers_media", "specialized_institutions"]
        for category in expected_categories:
            self.assertIn(category, sources, f"Missing source category: {category}")
            
        # Check tier prioritization
        self.assertIn("source_priorities", config)
        priorities = config["source_priorities"]
        self.assertIn("tier_1", priorities)
        
    def test_scraping_config_structure(self):
        """Test scraping configuration structure"""
        with open(self.configs_dir / "scraping_config.json", 'r', encoding='utf-8') as f:
            config = json.load(f)
            
        # Check scraping strategies
        self.assertIn("scraping_strategies", config)
        strategies = config["scraping_strategies"]
        self.assertIn("web_scraping", strategies)
        self.assertIn("api_scraping", strategies)
        
        # Check source-specific configs
        self.assertIn("source_specific_configs", config)
        
    def test_processing_config_structure(self):
        """Test processing configuration structure"""
        with open(self.configs_dir / "processing_config.json", 'r', encoding='utf-8') as f:
            config = json.load(f)
            
        # Check text processing
        self.assertIn("text_processing", config)
        text_processing = config["text_processing"]
        self.assertIn("encoding_handling", text_processing)
        self.assertIn("pashto_specific", text_processing)
        
    def test_sample_files_exist(self):
        """Test that sample files exist"""
        sample_file = self.config_dir / "samples" / "pashto_text_samples.md"
        self.assertTrue(sample_file.exists(), "Sample text file missing")
        
    def test_readme_exists(self):
        """Test that README file exists"""
        readme_file = self.config_dir / "README.md"
        self.assertTrue(readme_file.exists(), "README.md file missing")

def test_basic_functionality():
    """Test basic configuration loading and processing"""
    print("Testing basic functionality...")
    
    # Test config loading
    try:
        from configs.pashto_pipeline_example import PashtoConfigManager
        
        config_manager = PashtoConfigManager()
        print("✓ ConfigManager initialized successfully")
        
        # Test getting configuration
        main_config = config_manager.get("main")
        assert "project" in main_config
        print("✓ Main configuration accessible")
        
        # Test Pashto text processor initialization  
        from configs.pashto_pipeline_example import PashtoTextProcessor
        
        processor = PashtoTextProcessor(config_manager)
        print("✓ PashtoTextProcessor initialized successfully")
        
        # Test basic text processing
        test_text = "پښتو د پښتنو ژبه ده."
        result = processor.process_text(test_text, "test")
        
        assert result.content == test_text
        print(f"✓ Text processing works: lang={result.language}, quality={result.quality_score:.2f}")
        
    except ImportError as e:
        print(f"⚠ Cannot test basic functionality: {e}")
        print("  This is expected if dependencies are not installed")

def test_sample_texts():
    """Test processing of sample Pashto texts"""
    print("\nTesting sample Pashto texts...")
    
    sample_texts = [
        ("پښتو د پښتنو ژبه ده.", "basic"),
        ("د سولې د تاسیسولو لپاره، زموږ ټولو ته اړتیا ده چې د ټولنې د ښه والي په خاطر خپل ځانونه قرباني کړو.", "complex"),
        ("د کمپیوټر ټکنالوژۍ په ډېری برخو کې انقلاب رامنځته کړی.", "technical"),
        ("Hello world, this is mixed content with English.", "mixed")
    ]
    
    try:
        from configs.pashto_pipeline_example import PashtoTextProcessor, PashtoConfigManager
        
        config_manager = PashtoConfigManager()
        processor = PashtoTextProcessor(config_manager)
        
        for text, text_type in sample_texts:
            result = processor.process_text(text, f"sample_{text_type}")
            print(f"  {text_type:8} - Lang: {result.language:3}, Quality: {result.quality_score:.2f}, Words: {result.word_count}")
            
    except ImportError as e:
        print(f"⚠ Cannot test sample texts: {e}")

def main():
    """Run all tests"""
    print("Pashto Dataset Pipeline - Configuration Validation")
    print("=" * 60)
    
    # Test configuration structure
    print("1. Testing configuration file structure...")
    suite = unittest.TestLoader().loadTestsFromTestCase(TestPashtoConfig)
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    if result.wasSuccessful():
        print("\n✓ All configuration tests passed!")
    else:
        print(f"\n✗ {len(result.failures)} test failures, {len(result.errors)} errors")
        return 1
        
    # Test basic functionality
    test_basic_functionality()
    
    # Test sample texts
    test_sample_texts()
    
    print("\n" + "=" * 60)
    print("Configuration validation complete!")
    print("\nNext steps:")
    print("1. Install dependencies: pip install -r requirements.txt")
    print("2. Run the full example: python configs/pashto_pipeline_example.py")
    print("3. Review documentation: documentation/pashto_research_report.md")
    print("4. Customize configurations for your specific needs")
    
    return 0

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)