#!/bin/bash
# =====================================================
# Pashto Processing Pipeline - Installation Script
# =====================================================
#
# This script installs all dependencies and sets up
# the Pashto Processing Pipeline environment.
#
# Usage:
#   bash install.sh           # Install all dependencies
#   bash install.sh --dev     # Install with dev dependencies
#   bash install.sh --minimal # Install minimal dependencies only
# =====================================================

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Functions
print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check Python version
check_python() {
    print_status "Checking Python version..."
    
    if ! command -v python3 &> /dev/null; then
        print_error "Python 3 is not installed. Please install Python 3.8 or higher."
        exit 1
    fi
    
    python_version=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
    required_version="3.8"
    
    if [ "$(printf '%s\n' "$required_version" "$python_version" | sort -V | head -n1)" = "$required_version" ]; then 
        print_status "Python $python_version detected (>= $required_version) ✓"
    else
        print_error "Python $python_version is installed, but version >= $required_version is required."
        exit 1
    fi
}

# Create virtual environment
create_venv() {
    print_status "Creating virtual environment..."
    
    if [ -d "venv" ]; then
        print_warning "Virtual environment already exists. Skipping creation."
    else
        python3 -m venv venv
        print_status "Virtual environment created successfully ✓"
    fi
}

# Activate virtual environment
activate_venv() {
    print_status "Activating virtual environment..."
    source venv/bin/activate
    print_status "Virtual environment activated ✓"
}

# Install dependencies
install_dependencies() {
    local mode=$1
    
    print_status "Installing dependencies (mode: $mode)..."
    
    # Upgrade pip
    pip install --upgrade pip setuptools wheel
    
    if [ "$mode" = "minimal" ]; then
        # Install only core dependencies
        pip install numpy pandas pyyaml tqdm
        print_status "Minimal dependencies installed ✓"
    elif [ "$mode" = "dev" ]; then
        # Install all dependencies including dev tools
        pip install -r requirements.txt
        pip install -e ".[dev]"
        print_status "All dependencies (including dev tools) installed ✓"
    else
        # Install all production dependencies
        pip install -r requirements.txt
        pip install -e .
        print_status "Production dependencies installed ✓"
    fi
}

# Download NLTK data
download_nltk_data() {
    print_status "Downloading NLTK data..."
    
    python3 << EOF
import nltk
try:
    nltk.download('punkt', quiet=True)
    nltk.download('stopwords', quiet=True)
    print("NLTK data downloaded successfully")
except Exception as e:
    print(f"Warning: Could not download NLTK data: {e}")
EOF
    
    print_status "NLTK data downloaded ✓"
}

# Create necessary directories
create_directories() {
    print_status "Creating necessary directories..."
    
    mkdir -p data/raw
    mkdir -p data/processed
    mkdir -p models
    mkdir -p outputs
    mkdir -p logs
    
    # Create .gitkeep files to preserve empty directories
    touch data/raw/.gitkeep
    touch data/processed/.gitkeep
    touch models/.gitkeep
    touch outputs/.gitkeep
    touch logs/.gitkeep
    
    print_status "Directories created ✓"
}

# Main installation
main() {
    local install_mode="standard"
    
    # Parse arguments
    for arg in "$@"; do
        case $arg in
            --dev)
                install_mode="dev"
                shift
                ;;
            --minimal)
                install_mode="minimal"
                shift
                ;;
            --help|-h)
                echo "Usage: bash install.sh [--dev|--minimal]"
                echo "  --dev      Install with development dependencies"
                echo "  --minimal  Install minimal dependencies only"
                exit 0
                ;;
        esac
    done
    
    print_status "Starting Pashto Processing Pipeline installation..."
    echo ""
    
    check_python
    create_venv
    activate_venv
    install_dependencies "$install_mode"
    
    if [ "$install_mode" != "minimal" ]; then
        download_nltk_data
    fi
    
    create_directories
    
    echo ""
    print_status "============================================"
    print_status "Installation completed successfully! 🎉"
    print_status "============================================"
    echo ""
    print_status "To activate the environment, run:"
    echo "  source venv/bin/activate"
    echo ""
    print_status "To test the installation, run:"
    echo "  python examples/basic_usage.py"
    echo ""
}

# Run main function
main "$@"
