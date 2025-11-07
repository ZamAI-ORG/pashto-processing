#!/bin/bash
# Pashto Dataset Pipeline - Command Line Examples
# This script demonstrates various command-line operations

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Configuration
PIPELINE_CMD="pashto-pipeline"
CONFIG_DIR="examples/config"
DATA_DIR="examples/data"
SCRIPT_DIR="examples/scripts"

# Create necessary directories
create_directories() {
    log_info "Creating directory structure..."
    
    mkdir -p "$DATA_DIR"/{input,output,processed}
    mkdir -p "$SCRIPT_DIR"
    mkdir -p logs
    mkdir -p reports
    
    log_success "Directory structure created"
}

# Check if pipeline command is available
check_pipeline_command() {
    if ! command -v $PIPELINE_CMD &> /dev/null; then
        log_error "Pipeline command '$PIPELINE_CMD' not found"
        log_info "Please install the Pashto Dataset Pipeline:"
        log_info "  pip install pashto-dataset-pipeline"
        exit 1
    fi
    log_success "Pipeline command found: $($PIPELINE_CMD --version)"
}

# Create sample data
create_sample_data() {
    log_info "Creating sample Pashto data..."
    
    # Create sample text files
    cat > "$DATA_DIR/input/sample1.txt" << 'EOF'
زموږ ژبه د پښتو ژبه ده چې د افغانستان او پاکستان د خلکو ژبه ده.
دا ښه ژبه ده او موږ یې ډېر څیړو.
پښتو ژبه د نړۍ د ژبو څخه یوه ښه ژبه ده.
EOF

    cat > "$DATA_DIR/input/sample2.txt" << 'EOF'
موږ د ژبې څیړنه ډېر ښه کار دی.
زموږ د افغانستان تاریخ ډېر ښه دی.
د کابل ښار د افغانستان پلازمینه ده.
موږ د خپلو کلتور او ژبې خوښي لرو.
EOF

    cat > "$DATA_DIR/input/sample3.txt" << 'EOF'
This is English text mixed with Pashto: زموږ ژبه.
Visit http://example.com for more information.
Contact us at info@example.com
© 2025 All rights reserved.
EOF

    # Create sample JSON file
    cat > "$DATA_DIR/input/sample.json" << 'EOF'
[
  {
    "id": 1,
    "text": "زموږ د ژبې څیړنه ډېر ښه کار دی.",
    "source": "sample_data"
  },
  {
    "id": 2,
    "text": "پښتو شاعراني ډېر ښه دی.",
    "source": "poetry_data"
  }
]
EOF

    log_success "Sample data created in $DATA_DIR/input/"
}

# Basic processing example
basic_processing() {
    log_info "Running basic processing example..."
    
    $PIPELINE_CMD process \
        --input "$DATA_DIR/input/" \
        --output "$DATA_DIR/output/basic/" \
        --config "$CONFIG_DIR/basic_config.yaml" \
        --verbose
    
    if [ $? -eq 0 ]; then
        log_success "Basic processing completed"
    else
        log_error "Basic processing failed"
        return 1
    fi
}

# Web scraping example (simulation)
web_scraping_example() {
    log_info "Running web scraping configuration example..."
    
    # This would normally scrape real websites
    # For demo purposes, we'll simulate with existing data
    log_warning "Web scraping simulation - using sample data"
    
    $PIPELINE_CMD process \
        --input "$DATA_DIR/input/" \
        --output "$DATA_DIR/output/web_scraped/" \
        --config "$CONFIG_DIR/web_scraping.yaml" \
        --min-quality 0.5 \
        --verbose
    
    if [ $? -eq 0 ]; then
        log_success "Web scraping simulation completed"
    else
        log_error "Web scraping simulation failed"
        return 1
    fi
}

# Batch processing example
batch_processing_example() {
    log_info "Running batch processing example..."
    
    # Create more sample files for batch processing
    for i in {4..10}; do
        cat > "$DATA_DIR/input/batch_$i.txt" << EOF
Batch sample $i: زموږ د ژبې څیړنه ډېر ښه کار دی.
د افغانستان د ښارونو څیړنه ډېر ښه ده.
موږ د خپلو ښارونو څیړنه کوو.
EOF
    done
    
    $PIPELINE_CMD process \
        --input "$DATA_DIR/input/" \
        --output "$DATA_DIR/output/batch/" \
        --config "$CONFIG_DIR/batch_processing.yaml" \
        --workers 4 \
        --verbose
    
    if [ $? -eq 0 ]; then
        log_success "Batch processing completed"
    else
        log_error "Batch processing failed"
        return 1
    fi
}

# Quality assessment example
quality_assessment() {
    log_info "Running quality assessment example..."
    
    $PIPELINE_CMD quality-check \
        --input "$DATA_DIR/output/basic/" \
        --report \
        --output "reports/quality_report.html"
    
    if [ $? -eq 0 ]; then
        log_success "Quality assessment completed - report saved to reports/quality_report.html"
    else
        log_error "Quality assessment failed"
        return 1
    fi
}

# Statistics generation example
statistics_generation() {
    log_info "Generating statistics..."
    
    $PIPELINE_CMD stats \
        --input "$DATA_DIR/output/basic/" \
        --detailed \
        --output "reports/statistics.json"
    
    if [ $? -eq 0 ]; then
        log_success "Statistics generated - saved to reports/statistics.json"
    else
        log_error "Statistics generation failed"
        return 1
    fi
}

# Configuration validation
validate_configuration() {
    log_info "Validating configurations..."
    
    for config_file in "$CONFIG_DIR"/*.yaml; do
        if [ -f "$config_file" ]; then
            log_info "Validating $(basename "$config_file")..."
            $PIPELINE_CMD validate-config --file "$config_file"
            if [ $? -eq 0 ]; then
                log_success "  ✓ $(basename "$config_file") is valid"
            else
                log_error "  ✗ $(basename "$config_file") is invalid"
            fi
        fi
    done
}

# Performance monitoring example
performance_monitoring() {
    log_info "Running performance monitoring example..."
    
    $PIPELINE_CMD process \
        --input "$DATA_DIR/input/" \
        --output "$DATA_DIR/output/performance/" \
        --config "$CONFIG_DIR/basic_config.yaml" \
        --profile \
        --monitor-resources \
        --verbose
    
    if [ $? -eq 0 ]; then
        log_success "Performance monitoring completed"
    else
        log_error "Performance monitoring failed"
        return 1
    fi
}

# Export data example
export_data() {
    log_info "Exporting data to different formats..."
    
    # Export to CSV
    $PIPELINE_CMD export \
        --input "$DATA_DIR/output/basic/" \
        --output "$DATA_DIR/output/exports/" \
        --format csv
    
    # Export to XML
    $PIPELINE_CMD export \
        --input "$DATA_DIR/output/basic/" \
        --output "$DATA_DIR/output/exports/" \
        --format xml
    
    if [ $? -eq 0 ]; then
        log_success "Data export completed"
    else
        log_error "Data export failed"
        return 1
    fi
}

# Create custom script
create_custom_script() {
    log_info "Creating custom processing script..."
    
    cat > "$SCRIPT_DIR/custom_processing.sh" << 'EOF'
#!/bin/bash
# Custom processing script for specific use cases

INPUT_DIR="$1"
OUTPUT_DIR="$2"
CONFIG_FILE="$3"

if [ $# -ne 3 ]; then
    echo "Usage: $0 <input_dir> <output_dir> <config_file>"
    exit 1
fi

echo "Running custom processing..."
echo "Input: $INPUT_DIR"
echo "Output: $OUTPUT_DIR"
echo "Config: $CONFIG_FILE"

pashto-pipeline process \
    --input "$INPUT_DIR" \
    --output "$OUTPUT_DIR" \
    --config "$CONFIG_FILE" \
    --min-quality 0.8 \
    --require-pashto true \
    --remove-duplicates true \
    --verbose
EOF

    chmod +x "$SCRIPT_DIR/custom_processing.sh"
    log_success "Custom script created: $SCRIPT_DIR/custom_processing.sh"
}

# Run custom script example
run_custom_script() {
    log_info "Running custom processing script..."
    
    "$SCRIPT_DIR/custom_processing.sh" \
        "$DATA_DIR/input/" \
        "$DATA_DIR/output/custom/" \
        "$CONFIG_DIR/basic_config.yaml"
    
    if [ $? -eq 0 ]; then
        log_success "Custom script execution completed"
    else
        log_error "Custom script execution failed"
        return 1
    fi
}

# Cleanup function
cleanup() {
    log_info "Cleaning up temporary files..."
    
    # Remove temporary batch files
    rm -f "$DATA_DIR"/input/batch_*.txt
    
    # Archive logs
    if [ -d "logs" ] && [ "$(ls -A logs)" ]; then
        tar -czf "logs/archive_$(date +%Y%m%d_%H%M%S).tar.gz" logs/
        rm -f logs/*.log
    fi
    
    log_success "Cleanup completed"
}

# Show results summary
show_summary() {
    log_info "=== PROCESSING SUMMARY ==="
    
    echo
    log_info "Output directories created:"
    find "$DATA_DIR/output" -type d 2>/dev/null | while read dir; do
        echo "  $dir"
    done
    
    echo
    log_info "Generated reports:"
    if [ -d "reports" ] && [ "$(ls -A reports)" ]; then
        ls -la reports/ | grep -v "^d" | while read -r line; do
            echo "  $line"
        done
    fi
    
    echo
    log_info "Sample commands for further use:"
    echo "  # Process new data"
    echo "  pashto-pipeline process --input new_data/ --output processed/ --config $CONFIG_DIR/basic_config.yaml"
    echo
    echo "  # Check quality"
    echo "  pashto-pipeline quality-check --input processed/ --report"
    echo
    echo "  # Generate statistics"
    echo "  pashto-pipeline stats --input processed/ --detailed"
    echo
    echo "  # Export to different formats"
    echo "  pashto-pipeline export --input processed/ --output exports/ --format csv"
}

# Main execution
main() {
    echo "========================================"
    echo "Pashto Dataset Pipeline - CLI Examples"
    echo "========================================"
    echo
    
    # Create directories
    create_directories
    
    # Check pipeline installation
    check_pipeline_command
    
    # Create sample data
    create_sample_data
    
    # Validate configurations
    log_info "Validating all configurations..."
    validate_configuration
    echo
    
    # Run examples
    log_info "Starting processing examples..."
    echo
    
    # Basic processing
    basic_processing
    echo
    
    # Web scraping (simulation)
    web_scraping_example
    echo
    
    # Quality assessment
    quality_assessment
    echo
    
    # Statistics
    statistics_generation
    echo
    
    # Export data
    export_data
    echo
    
    # Batch processing (optional, takes longer)
    if [ "$1" = "--batch" ] || [ "$1" = "--full" ]; then
        batch_processing_example
        echo
    fi
    
    # Performance monitoring (optional)
    if [ "$1" = "--performance" ] || [ "$1" = "--full" ]; then
        performance_monitoring
        echo
    fi
    
    # Custom script
    create_custom_script
    run_custom_script
    echo
    
    # Show summary
    show_summary
    
    # Cleanup
    cleanup
    
    echo
    log_success "All examples completed successfully!"
    log_info "Check the output directories for results"
    echo "========================================"
}

# Handle script arguments
case "$1" in
    --help|-h)
        echo "Pashto Dataset Pipeline - CLI Examples"
        echo
        echo "Usage: $0 [--options]"
        echo
        echo "Options:"
        echo "  --help, -h         Show this help message"
        echo "  --batch            Include batch processing example"
        echo "  --performance      Include performance monitoring example"
        echo "  --full             Run all examples (batch + performance)"
        echo "  --cleanup-only     Run cleanup only"
        echo
        echo "Examples:"
        echo "  $0                 Run basic examples"
        echo "  $0 --full          Run all examples"
        echo "  $0 --batch         Include batch processing"
        echo
        exit 0
        ;;
    --cleanup-only)
        cleanup
        exit 0
        ;;
    *)
        main "$@"
        ;;
esac