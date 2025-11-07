# Installation Guide

This guide provides detailed instructions for installing the Pashto Dataset Pipeline in various environments.

## 📋 Prerequisites

### System Requirements
- **Operating System**: Linux, macOS, Windows 10+
- **Python**: 3.8 or higher
- **Memory**: Minimum 4GB RAM (8GB+ recommended for large datasets)
- **Storage**: 2GB free disk space (more for datasets)
- **Internet**: Required for initial installation and web scraping

### Software Dependencies
- **Python 3.8+** with pip or conda
- **Git** (for source installation)
- **C++ Compiler** (for building some dependencies)

## 🐍 Python Environment Setup

### Option 1: Using pip (Recommended)

#### 1. Create Virtual Environment
```bash
# Create virtual environment
python -m venv pashto-env

# Activate virtual environment
# On Linux/macOS:
source pashto-env/bin/activate

# On Windows:
pashto-env\Scripts\activate
```

#### 2. Upgrade pip and Install
```bash
# Upgrade pip
pip install --upgrade pip

# Install Pashto Dataset Pipeline
pip install pashto-dataset-pipeline
```

### Option 2: Using conda

```bash
# Create conda environment
conda create -n pashto-pipeline python=3.9
conda activate pashto-pipeline

# Install
conda install -c conda-forge pashto-dataset-pipeline
```

### Option 3: Development Installation

```bash
# Clone repository
git clone https://github.com/your-org/pashto-dataset-pipeline.git
cd pashto-dataset-pipeline

# Create virtual environment
python -m venv dev-env
source dev-env/bin/activate  # Linux/macOS
# dev-env\Scripts\activate    # Windows

# Install in development mode
pip install -e .
pip install -r requirements-dev.txt
```

## 📦 Installation Verification

### Quick Test
```python
# Test installation
python -c "import pashto_pipeline; print('Installation successful!')"
```

### Run Unit Tests
```bash
# Run tests
pashto-pipeline test

# Or with pytest directly
pytest tests/ -v
```

## 🛠️ Platform-Specific Instructions

### Linux (Ubuntu/Debian)

```bash
# Install system dependencies
sudo apt update
sudo apt install python3-dev python3-pip git build-essential

# Install Python packages
pip3 install --user pashto-dataset-pipeline
```

### Linux (CentOS/RHEL/Fedora)

```bash
# Install system dependencies
sudo yum install python3-devel python3-pip git gcc
# OR for newer versions:
sudo dnf install python3-devel python3-pip git gcc

# Install Python packages
pip3 install --user pashto-dataset-pipeline
```

### macOS

```bash
# Install Homebrew (if not installed)
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Install Python and dependencies
brew install python@3.9 git

# Install pipeline
pip3 install pashto-dataset-pipeline
```

### Windows

#### Using PowerShell (Administrator)
```powershell
# Install Python from Microsoft Store or python.org
# Install pipx for clean package management
python -m pip install --upgrade pip
pip install --user pashto-dataset-pipeline
```

#### Using Chocolatey
```powershell
# Install Chocolatey (if not installed)
Set-ExecutionPolicy Bypass -Scope Process -Force; [System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072; iex ((New-Object System.Net.WebClient).DownloadString('https://chocolatey.org/install.ps1'))

# Install dependencies
choco install python3 git

# Install pipeline
pip install pashto-dataset-pipeline
```

## 🐳 Docker Installation

### Using Pre-built Image

```bash
# Pull and run
docker run -it -v $(pwd):/workspace pashto-dataset-pipeline:latest
```

### Building Custom Image

```dockerfile
# Dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
RUN pip install -e .

CMD ["pashto-pipeline", "--help"]
```

```bash
# Build and run
docker build -t pashto-pipeline-custom .
docker run -it -v $(pwd):/workspace pashto-pipeline-custom
```

## ⚙️ Configuration Setup

### Create Configuration Directory
```bash
# Create config directory
mkdir -p ~/.config/pashto-pipeline
cp examples/config/basic_config.yaml ~/.config/pashto-pipeline/
```

### Environment Variables (Optional)
```bash
# Add to ~/.bashrc or ~/.zshrc
export PASHTOPIPELINE_CONFIG_DIR="$HOME/.config/pashto-pipeline"
export PASHTOPIPELINE_LOG_LEVEL="INFO"
export PASHTOPIPELINE_MAX_WORKERS="4"
```

## 🔧 Advanced Installation

### GPU Support (Optional)

For accelerated processing with GPU:

```bash
# Install with GPU support
pip install pashto-dataset-pipeline[gpu]

# Verify GPU installation
python -c "import torch; print(f'CUDA available: {torch.cuda.is_available()}')"
```

### Full Feature Installation

```bash
# Install all optional dependencies
pip install pashto-dataset-pipeline[all]

# Or specific extras
pip install pashto-dataset-pipeline[web,ml,database]
```

### Development Dependencies

```bash
# Install development tools
pip install -e ".[dev]"
pip install -e ".[test]"
pip install -e ".[docs]"
```

## 📊 Memory and Performance Optimization

### For Large Datasets (64GB+ RAM)
```bash
# Install with optimization flags
export PASCAL_PIPELINE_OPTIMIZE=1
pip install pashto-dataset-pipeline
```

### For Limited Memory (4GB RAM)
```bash
# Install lightweight version
pip install pashto-dataset-pipeline[lightweight]
```

## 🚀 Post-Installation

### 1. Verify Installation
```bash
# Check version
pashto-pipeline --version

# List available commands
pashto-pipeline --help

# Test with sample data
pashto-pipeline test-data --generate --output sample_data/
```

### 2. Create Project Structure
```bash
# Create new project
pashto-pipeline create-project my_pashto_project
cd my_pashto_project

# Directory structure
ls -la
# config/
# data/
# output/
# scripts/
# tests/
```

### 3. Run Your First Pipeline
```bash
# Process sample data
pashto-pipeline process \
  --input data/raw/ \
  --output data/processed/ \
  --config config/basic_config.yaml
```

## ❗ Common Installation Issues

### Python Version Issues
```bash
# Check Python version
python --version

# If using multiple Python versions
python3.9 -m pip install pashto-dataset-pipeline
```

### Permission Issues
```bash
# Install to user directory
pip install --user pashto-dataset-pipeline

# Or use virtual environment
python -m venv myenv
source myenv/bin/activate
pip install pashto-dataset-pipeline
```

### Network/Firewall Issues
```bash
# Use alternative index
pip install -i https://pypi.org/simple/ pashto-dataset-pipeline

# With trusted host
pip install --trusted-host pypi.org --trusted-host pypi.python.org pashto-dataset-pipeline
```

### Platform-Specific Issues

#### Windows
- Ensure Visual C++ Build Tools are installed
- Use Command Prompt as Administrator if needed
- Check Windows Defender exclusions for pip cache

#### macOS
- Install Xcode command line tools: `xcode-select --install`
- Use Homebrew for system dependencies

#### Linux
- Install build essentials: `sudo apt install build-essential`
- Check Python development headers: `python3-dev`

## 🆘 Getting Help

If you encounter installation issues:

1. Check the [Troubleshooting Guide](troubleshooting/common_issues.md)
2. Search [existing issues](https://github.com/your-org/pashto-dataset-pipeline/issues)
3. Create a new issue with your system information

### System Information Collection
```bash
# Collect system info for debugging
pashto-pipeline system-info

# Generate environment report
python -c "import platform, sys; print(f'OS: {platform.system()}, Python: {sys.version}')"
```

## 🔄 Updates and Maintenance

### Updating to Latest Version
```bash
# Update to latest version
pip install --upgrade pashto-dataset-pipeline

# Update with all dependencies
pip install --upgrade --force-reinstall pashto-dataset-pipeline
```

### Checking for Updates
```bash
# Check current version
pashto-pipeline --version

# List outdated packages
pip list --outdated
```

---

**Next Steps**: After installation, proceed to the [Quick Start Guide](quick_start.md) to process your first dataset.