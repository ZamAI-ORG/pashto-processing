#!/bin/bash

# 🚀 PASHT DATASET PIPELINE - AUTOMATED SETUP SCRIPT
# =================================================
# 
# This script automates the complete setup of the Pashto Dataset Creation Pipeline
# including dependency installation, system configuration, and validation.
#
# Author: MiniMax Agent
# Version: 1.0.0
# Created: 2025-11-06
#
# Usage: chmod +x setup.sh && ./setup.sh

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Script configuration
PYTHON_MIN_VERSION="3.8"
PIP_MIN_VERSION="21.0"

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_header() {
    echo -e "${PURPLE}"
    echo "=================================================================="
    echo "🚀 PASHT DATASET CREATION PIPELINE - SETUP SCRIPT"
    echo "=================================================================="
    echo -e "${NC}"
}

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to check Python version
check_python() {
    print_status "Checking Python version..."
    
    if ! command_exists python3; then
        print_error "Python 3 is not installed. Please install Python 3.8 or higher."
        exit 1
    fi
    
    PYTHON_VERSION=$(python3 -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
    
    if ! python3 -c "import sys; exit(0 if sys.version_info >= (3, 8) else 1)"; then
        print_error "Python 3.8 or higher is required. Found: $PYTHON_VERSION"
        exit 1
    fi
    
    print_success "Python $PYTHON_VERSION found"
}

# Function to check pip
check_pip() {
    print_status "Checking pip..."
    
    if ! command_exists pip3; then
        print_error "pip3 is not installed. Please install pip."
        exit 1
    fi
    
    PIP_VERSION=$(pip3 --version | cut -d' ' -f2)
    print_success "pip $PIP_VERSION found"
}

# Function to create virtual environment
create_venv() {
    print_status "Creating Python virtual environment..."
    
    if [ ! -d "venv" ]; then
        python3 -m venv venv
        print_success "Virtual environment created"
    else
        print_warning "Virtual environment already exists"
    fi
    
    # Activate virtual environment
    source venv/bin/activate
    print_success "Virtual environment activated"
}

# Function to upgrade pip
upgrade_pip() {
    print_status "Upgrading pip..."
    pip install --upgrade pip
    print_success "pip upgraded"
}

# Function to install Python dependencies
install_dependencies() {
    print_status "Installing Python dependencies..."
    
    # Install core dependencies first
    pip install --upgrade pip setuptools wheel
    
    # Install from requirements.txt
    if [ -f "requirements.txt" ]; then
        pip install -r requirements.txt
    else
        print_error "requirements.txt not found!"
        exit 1
    fi
    
    print_success "Python dependencies installed"
}

# Function to install system dependencies
install_system_deps() {
    print_status "Installing system dependencies..."
    
    # Detect OS
    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        # Linux
        print_status "Detected Linux system"
        
        # Check if running as root or with sudo
        if [ "$EUID" -eq 0 ]; then
            print_status "Installing system packages with root privileges..."
            
            # Update package list
            apt-get update -qq
            
            # Install required system packages
            apt-get install -y \
                python3-dev \
                python3-pip \
                build-essential \
                curl \
                wget \
                git \
                unzip \
                software-properties-common \
                apt-transport-https \
                ca-certificates \
                gnupg \
                lsb-release
                
            # Install Tesseract OCR with Pashto support
            add-apt-repository -y ppa:alex-p/tesseract-ocr
            apt-get update
            apt-get install -y tesseract-ocr tesseract-ocr-pus
            
            # Install additional tools
            apt-get install -y \
                poppler-utils \
                pandoc \
                vim \
                nano
            
            print_success "System packages installed"
        else
            print_warning "Not running as root. Some system packages may need manual installation."
            print_warning "Please install the following manually:"
            print_warning "  - tesseract-ocr with Pashto language support"
            print_warning "  - poppler-utils (for PDF processing)"
            print_warning "  - build-essential (for compiling Python packages)"
        fi
        
    elif [[ "$OSTYPE" == "darwin"* ]]; then
        # macOS
        print_status "Detected macOS system"
        
        if command_exists brew; then
            brew update
            brew install tesseract python3
            # Install Tesseract languages
            brew install tesseract-lang
        else
            print_warning "Homebrew not found. Please install Homebrew first:"
            print_warning "/bin/bash -c \"\$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)\""
        fi
        
    else
        print_warning "Unknown operating system: $OSTYPE"
        print_warning "Please install system dependencies manually."
    fi
}

# Function to download NLTK data
download_nltk_data() {
    print_status "Downloading NLTK data..."
    
    python3 -c "
import nltk
nltk.download('punkt', quiet=True)
nltk.download('stopwords', quiet=True)
nltk.download('averaged_perceptron_tagger', quiet=True)
nltk.download('wordnet', quiet=True)
print('NLTK data downloaded successfully')
"
    
    print_success "NLTK data downloaded"
}

# Function to download spaCy model
download_spacy_model() {
    print_status "Downloading spaCy model..."
    
    python3 -c "
import spacy
try:
    nlp = spacy.load('en_core_web_sm')
    print('English spaCy model already available')
except IOError:
    print('Downloading English spaCy model...')
    spacy.cli.download('en_core_web_sm')
    print('English spaCy model downloaded')
"
    
    print_success "spaCy model prepared"
}

# Function to create necessary directories
create_directories() {
    print_status "Creating necessary directories..."
    
    mkdir -p data/raw/web_data
    mkdir -p data/raw/pdf_data
    mkdir -p data/processed
    mkdir -p data/final
    mkdir -p logs
    mkdir -p configs
    mkdir -p output
    
    print_success "Directories created"
}

# Function to setup configuration files
setup_config() {
    print_status "Setting up configuration files..."
    
    # Copy configuration templates if they don't exist
    if [ ! -f "configs/main_config.json" ]; then
        cp config/main_config.json configs/ 2>/dev/null || echo "No main config found, skipping..."
    fi
    
    if [ ! -f "configs/source_config.json" ]; then
        cp config/source_config.json configs/ 2>/dev/null || echo "No source config found, skipping..."
    fi
    
    print_success "Configuration files setup"
}

# Function to validate installation
validate_installation() {
    print_status "Validating installation..."
    
    python3 -c "
import sys
import importlib.util

modules = [
    'pandas', 'numpy', 'requests', 'beautifulsoup4', 
    'PyPDF2', 'nltk', 'transformers', 'datasets',
    'yaml', 'tqdm'
]

failed_modules = []
for module in modules:
    if importlib.util.find_spec(module) is None:
        failed_modules.append(module)

if failed_modules:
    print(f'Failed to import: {failed_modules}')
    sys.exit(1)
else:
    print('All required modules imported successfully')
"
    
    if [ $? -eq 0 ]; then
        print_success "Installation validation passed"
    else
        print_error "Installation validation failed"
        exit 1
    fi
}

# Function to run tests
run_tests() {
    print_status "Running pipeline tests..."
    
    if [ -f "test_pipeline.py" ]; then
        python3 test_pipeline.py
        if [ $? -eq 0 ]; then
            print_success "Pipeline tests passed"
        else
            print_warning "Some pipeline tests failed"
        fi
    else
        print_warning "Test script not found, skipping tests"
    fi
}

# Function to create startup script
create_startup_script() {
    print_status "Creating startup script..."
    
    cat > start_pipeline.sh << 'EOF'
#!/bin/bash
# Pashto Dataset Pipeline Startup Script

# Activate virtual environment
source venv/bin/activate

# Change to script directory
cd "$(dirname "$0")"

echo "🚀 Starting Pashto Dataset Pipeline..."

# Run the pipeline
python3 main_pipeline.py "$@"
EOF
    
    chmod +x start_pipeline.sh
    print_success "Startup script created: start_pipeline.sh"
}

# Function to display usage information
show_usage() {
    echo -e "${CYAN}"
    echo "📋 USAGE INFORMATION"
    echo "==================="
    echo -e "${NC}"
    echo "To start the pipeline:"
    echo "  ./start_pipeline.sh                    # Run full pipeline"
    echo "  ./start_pipeline.sh --demo             # Run demonstration"
    echo "  ./start_pipeline.sh --test             # Run tests"
    echo ""
    echo "To activate the environment manually:"
    echo "  source venv/bin/activate"
    echo ""
    echo "Output files will be created in: ./output/"
    echo "Logs will be saved in: ./logs/"
}

# Main setup function
main() {
    print_header
    
    print_status "Starting setup process..."
    echo ""
    
    # Check prerequisites
    check_python
    check_pip
    
    # Create and setup virtual environment
    create_venv
    upgrade_pip
    
    # Install dependencies
    install_dependencies
    install_system_deps
    
    # Download data and models
    download_nltk_data
    download_spacy_model
    
    # Setup directories and configuration
    create_directories
    setup_config
    
    # Validate installation
    validate_installation
    run_tests
    
    # Create startup script
    create_startup_script
    
    echo ""
    print_success "🎉 SETUP COMPLETED SUCCESSFULLY!"
    echo ""
    
    # Show usage information
    show_usage
    
    echo ""
    print_status "The Pashto Dataset Creation Pipeline is ready to use!"
    print_status "For help and documentation, see the README.md file."
    echo ""
}

# Handle script arguments
case "${1:-}" in
    --help|-h)
        echo "Pashto Dataset Pipeline Setup Script"
        echo ""
        echo "Usage: $0 [options]"
        echo ""
        echo "Options:"
        echo "  --help, -h     Show this help message"
        echo "  --system-only  Install only system dependencies"
        echo "  --python-only  Install only Python dependencies"
        echo ""
        exit 0
        ;;
    --system-only)
        install_system_deps
        exit 0
        ;;
    --python-only)
        check_python
        check_pip
        create_venv
        upgrade_pip
        install_dependencies
        download_nltk_data
        download_spacy_model
        exit 0
        ;;
esac

# Run main setup
main "$@"