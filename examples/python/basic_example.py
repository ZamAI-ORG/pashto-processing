#!/usr/bin/env python3
"""
Basic Example: Using the Pashto Dataset Pipeline

This example demonstrates the basic usage of the Pashto Dataset Pipeline
with step-by-step explanations for new users.
"""

import os
import sys
import json
import logging
from pathlib import Path
from typing import List, Dict, Any

# Import pipeline components
try:
    from pashto_pipeline import Pipeline, Config
    from pashto_pipeline.exceptions import PipelineError
except ImportError:
    print("Error: Pashto Pipeline not installed.")
    print("Install it with: pip install pashto-dataset-pipeline")
    sys.exit(1)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class BasicPipelineExample:
    """
    Basic example of using the Pashto Dataset Pipeline.
    
    This class demonstrates:
    - Loading configuration
    - Processing data
    - Handling results
    - Error handling
    """
    
    def __init__(self, config_path: str = "examples/config/basic_config.yaml"):
        """
        Initialize the example.
        
        Args:
            config_path: Path to configuration file
        """
        self.config_path = config_path
        self.config = None
        self.pipeline = None
        self.setup()
    
    def setup(self):
        """Setup pipeline with configuration."""
        try:
            logger.info("Setting up Pashto Pipeline...")
            
            # Load configuration
            if not os.path.exists(self.config_path):
                raise FileNotFoundError(f"Configuration file not found: {self.config_path}")
            
            self.config = Config.from_file(self.config_path)
            logger.info(f"Configuration loaded from: {self.config_path}")
            
            # Create pipeline
            self.pipeline = Pipeline(self.config)
            logger.info("Pipeline created successfully")
            
            # Validate configuration
            if self.config.validate():
                logger.info("Configuration validation passed")
            else:
                raise PipelineError("Configuration validation failed")
                
        except Exception as e:
            logger.error(f"Setup failed: {e}")
            raise
    
    def create_sample_data(self, directory: str) -> None:
        """
        Create sample Pashto data for demonstration.
        
        Args:
            directory: Directory to create sample data in
        """
        logger.info(f"Creating sample data in: {directory}")
        
        # Create directory
        os.makedirs(directory, exist_ok=True)
        
        # Sample Pashto texts
        sample_texts = [
            "زموږ ژبه د پښتو ژبه ده چې د افغانستان او پاکستان د خلکو ژبه ده.",
            "دا ښه ژبه ده او موږ یې ډېر څیړو.",
            "پښتو ژبه د نړۍ د ژبو څخه یوه ښه ژبه ده.",
            "موږ د ژبې څیړنه ډېر ښه کار دی.",
            "دا څیړنه به زموږ ژبه ډېر ښه کړي.",
            "زموږ د افغانستان تاریخ ډېر ښه دی.",
            "د کابل ښار د افغانستان پلازمینه ده.",
            "موږ د خپلو کلتور او ژبې خوښي لرو.",
            "پښتو شاعراني ډېر ښه دی.",
            "زموږ د لیکلو هنر ډېر ښه دی."
        ]
        
        # Create text files
        for i, text in enumerate(sample_texts, 1):
            file_path = os.path.join(directory, f"text_{i:02d}.txt")
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(text)
        
        # Create a JSON file with mixed content
        json_data = [
            {
                "id": 1,
                "text": "زموږ د ژبې څیړنه ډېر ښه کار دی.",
                "metadata": {
                    "source": "sample_data",
                    "type": "text"
                }
            },
            {
                "id": 2,
                "text": "This is English text mixed with Pashto: زموږ ژبه.",
                "metadata": {
                    "source": "mixed_data",
                    "type": "bilingual"
                }
            },
            {
                "id": 3,
                "text": "URL: http://example.com - زموږ ژبه ښه ده",
                "metadata": {
                    "source": "web_data",
                    "type": "url_content"
                }
            }
        ]
        
        json_path = os.path.join(directory, "mixed_content.json")
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(json_data, f, ensure_ascii=False, indent=2)
        
        logger.info(f"Created {len(sample_texts)} text files and 1 JSON file")
    
    def process_data(self, input_dir: str, output_dir: str) -> Dict[str, Any]:
        """
        Process data using the pipeline.
        
        Args:
            input_dir: Input directory
            output_dir: Output directory
            
        Returns:
            Processing results
        """
        logger.info(f"Processing data from {input_dir} to {output_dir}")
        
        try:
            # Create output directory
            os.makedirs(output_dir, exist_ok=True)
            
            # Run pipeline
            result = self.pipeline.run(input_dir, output_dir)
            
            # Log results
            logger.info("Processing completed successfully!")
            logger.info(f"Total items processed: {result.total_processed}")
            logger.info(f"Items passed filters: {result.total_passed}")
            logger.info(f"Items filtered out: {result.total_filtered}")
            logger.info(f"Average quality score: {result.quality_score:.3f}")
            logger.info(f"Processing time: {result.processing_time:.2f} seconds")
            
            return {
                "total_processed": result.total_processed,
                "total_passed": result.total_passed,
                "total_filtered": result.total_filtered,
                "quality_score": result.quality_score,
                "processing_time": result.processing_time,
                "output_files": result.output_files
            }
            
        except PipelineError as e:
            logger.error(f"Pipeline error: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error during processing: {e}")
            raise
    
    def analyze_results(self, output_dir: str) -> Dict[str, Any]:
        """
        Analyze processing results.
        
        Args:
            output_dir: Output directory
            
        Returns:
            Analysis results
        """
        logger.info("Analyzing processing results...")
        
        analysis = {
            "output_files": [],
            "statistics": {},
            "quality_distribution": {},
            "language_analysis": {}
        }
        
        try:
            # Find output files
            for root, dirs, files in os.walk(output_dir):
                for file in files:
                    if file.endswith(('.json', '.csv', '.xml')):
                        file_path = os.path.join(root, file)
                        analysis["output_files"].append(file_path)
            
            # Analyze JSON output
            for file_path in analysis["output_files"]:
                if file_path.endswith('.json'):
                    with open(file_path, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                    
                    if 'data' in data:
                        texts = data['data']
                        analysis["statistics"]["total_records"] = len(texts)
                        
                        # Quality score distribution
                        quality_scores = [item['metadata'].get('quality_score', 0) 
                                        for item in texts if 'metadata' in item]
                        
                        if quality_scores:
                            analysis["quality_distribution"] = {
                                "min": min(quality_scores),
                                "max": max(quality_scores),
                                "mean": sum(quality_scores) / len(quality_scores),
                                "high_quality_count": sum(1 for q in quality_scores if q >= 0.7),
                                "medium_quality_count": sum(1 for q in quality_scores if 0.5 <= q < 0.7),
                                "low_quality_count": sum(1 for q in quality_scores if q < 0.5)
                            }
            
            logger.info("Analysis completed")
            return analysis
            
        except Exception as e:
            logger.error(f"Analysis failed: {e}")
            return analysis
    
    def demonstrate_advanced_features(self, output_dir: str) -> None:
        """
        Demonstrate advanced pipeline features.
        
        Args:
            output_dir: Output directory
        """
        logger.info("Demonstrating advanced features...")
        
        # 1. Process a single file
        single_file = os.path.join(output_dir, "single_file_result.json")
        logger.info("Processing single file...")
        
        try:
            # This would process a specific file
            # result = self.pipeline.process_file("path/to/specific/file.txt")
            logger.info("Single file processing demo (not executed)")
        except Exception as e:
            logger.error(f"Single file processing failed: {e}")
        
        # 2. Quality assessment
        logger.info("Performing quality assessment...")
        try:
            # result = self.pipeline.assess_quality(output_dir)
            logger.info("Quality assessment demo (not executed)")
        except Exception as e:
            logger.error(f"Quality assessment failed: {e}")
        
        # 3. Statistics generation
        logger.info("Generating statistics...")
        try:
            # stats = self.pipeline.get_statistics()
            logger.info("Statistics generation demo (not executed)")
        except Exception as e:
            logger.error(f"Statistics generation failed: {e}")
    
    def run_example(self) -> None:
        """
        Run the complete example workflow.
        """
        logger.info("="*50)
        logger.info("Starting Pashto Pipeline Basic Example")
        logger.info("="*50)
        
        # Setup directories
        input_dir = "examples/data/input"
        output_dir = "examples/data/output"
        temp_dir = "examples/data/temp"
        
        try:
            # Step 1: Create sample data
            self.create_sample_data(input_dir)
            
            # Step 2: Process data
            results = self.process_data(input_dir, output_dir)
            
            # Step 3: Analyze results
            analysis = self.analyze_results(output_dir)
            
            # Step 4: Demonstrate advanced features
            self.demonstrate_advanced_features(output_dir)
            
            # Step 5: Print summary
            self.print_summary(results, analysis)
            
            logger.info("="*50)
            logger.info("Example completed successfully!")
            logger.info("="*50)
            
        except Exception as e:
            logger.error(f"Example failed: {e}")
            raise
    
    def print_summary(self, results: Dict, analysis: Dict) -> None:
        """
        Print a summary of the example results.
        
        Args:
            results: Processing results
            analysis: Analysis results
        """
        print("\n" + "="*60)
        print("PASHT0 DATASET PIPELINE - EXAMPLE SUMMARY")
        print("="*60)
        
        print(f"\n📊 PROCESSING RESULTS:")
        print(f"   • Total items processed: {results['total_processed']}")
        print(f"   • Items passed filters: {results['total_passed']}")
        print(f"   • Items filtered out: {results['total_filtered']}")
        print(f"   • Quality score: {results['quality_score']:.3f}")
        print(f"   • Processing time: {results['processing_time']:.2f}s")
        
        if 'quality_distribution' in analysis and analysis['quality_distribution']:
            qd = analysis['quality_distribution']
            print(f"\n🎯 QUALITY DISTRIBUTION:")
            print(f"   • High quality (≥0.7): {qd.get('high_quality_count', 0)} items")
            print(f"   • Medium quality (0.5-0.7): {qd.get('medium_quality_count', 0)} items")
            print(f"   • Low quality (<0.5): {qd.get('low_quality_count', 0)} items")
        
        print(f"\n📁 OUTPUT FILES:")
        for file_path in analysis.get('output_files', []):
            print(f"   • {file_path}")
        
        print(f"\n💡 NEXT STEPS:")
        print(f"   • Check the output files in: {os.path.abspath('examples/data/output')}")
        print(f"   • Review the configuration: {self.config_path}")
        print(f"   • Try customizing the configuration for your needs")
        print(f"   • Explore advanced features in other examples")
        
        print("="*60)

def main():
    """
    Main function to run the example.
    """
    # Parse command line arguments
    if len(sys.argv) > 1:
        config_path = sys.argv[1]
    else:
        config_path = "examples/config/basic_config.yaml"
    
    try:
        # Create and run example
        example = BasicPipelineExample(config_path)
        example.run_example()
        
    except KeyboardInterrupt:
        logger.info("Example interrupted by user")
    except Exception as e:
        logger.error(f"Example failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()