"""
Setup script for Pashto Processing Pipeline.
"""

from setuptools import setup, find_packages
import os

# Read README for long description
def read_readme():
    readme_path = os.path.join(os.path.dirname(__file__), 'README.md')
    if os.path.exists(readme_path):
        with open(readme_path, 'r', encoding='utf-8') as f:
            return f.read()
    return "Pashto Processing Pipeline"

# Read requirements
def read_requirements():
    requirements_path = os.path.join(os.path.dirname(__file__), 'requirements.txt')
    requirements = []
    if os.path.exists(requirements_path):
        with open(requirements_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                # Skip comments and empty lines
                if line and not line.startswith('#'):
                    requirements.append(line)
    return requirements

setup(
    name="pashto-processing-pipeline",
    version="1.0.0",
    author="Pashto Processing Team",
    author_email="dev@pashto-dataset.org",
    description="Comprehensive text processing pipeline for Pashto language",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    url="https://github.com/tasal9/Pashto-Processing-pipeline",
    
    # Package information
    packages=find_packages(include=['pashto_pipeline', 'pashto_pipeline.*']),
    
    # Dependencies
    install_requires=read_requirements(),
    
    # Extra dependencies for development
    extras_require={
        'dev': [
            'pytest>=7.1.0',
            'pytest-cov>=3.0.0',
            'black>=22.0.0',
            'flake8>=5.0.0',
            'isort>=5.10.0',
            'mypy>=0.950'
        ],
        'test': [
            'pytest>=7.1.0',
            'pytest-cov>=3.0.0',
            'pytest-xdist>=2.5.0',
            'hypothesis>=6.54.0'
        ],
        'docs': [
            'sphinx>=4.0.0',
            'sphinx-rtd-theme>=0.5.0'
        ],
        'ml': [
            'torch>=1.12.0',
            'sentence-transformers>=2.2.0',
            'faiss-cpu>=1.7.0'
        ]
    },
    
    # Entry points for command line tools
    # Note: CLI tools are available in code/pashto_dataset package
    # entry_points={
    #     'console_scripts': [
    #         'pashto-pipeline=code.pashto_dataset.pipeline.main:main',
    #     ]
    # },
    
    # Python version requirement
    python_requires=">=3.8",
    
    # Package classification
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Text Processing :: Linguistic",
    ],
    
    # Keywords for package discovery
    keywords=[
        "pashto",
        "nlp",
        "text-processing",
        "pipeline",
        "dataset",
        "machine-learning",
        "natural-language-processing"
    ],
    
    # Project URLs
    project_urls={
        "Bug Reports": "https://github.com/tasal9/Pashto-Processing-pipeline/issues",
        "Source": "https://github.com/tasal9/Pashto-Processing-pipeline",
    },
    
    # Include data files
    include_package_data=True,
    
    # Exclude certain files from distribution
    zip_safe=False,
)
