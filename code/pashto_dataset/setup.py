"""
Setup script for Pashto Dataset Pipeline Orchestration System.
"""

from setuptools import setup, find_packages
import os

# Read README for long description
def read_readme():
    readme_path = os.path.join(os.path.dirname(__file__), 'README.md')
    if os.path.exists(readme_path):
        with open(readme_path, 'r', encoding='utf-8') as f:
            return f.read()
    return "Pashto Dataset Pipeline Orchestration System"

# Read requirements
def read_requirements():
    requirements_path = os.path.join(os.path.dirname(__file__), 'requirements.txt')
    if os.path.exists(requirements_path):
        with open(requirements_path, 'r', encoding='utf-8') as f:
            return [line.strip() for line in f if line.strip() and not line.startswith('#')]
    return [
        "psutil>=5.8.0",
        "schedule>=1.1.0",
        "pandas>=1.3.0",
        "numpy>=1.21.0"
    ]

setup(
    name="pashto-dataset-pipeline",
    version="1.0.0",
    author="Pipeline Development Team",
    author_email="dev@pashto-dataset.org",
    description="Comprehensive pipeline orchestration system for Pashto dataset processing",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    url="https://github.com/pashto-dataset/pipeline",
    
    # Package information
    packages=find_packages(),
    package_dir={'': '.'},
    
    # Dependencies
    install_requires=read_requirements(),
    
    # Extra dependencies for development
    extras_require={
        'dev': [
            'pytest>=6.2.0',
            'pytest-cov>=2.12.0',
            'black>=21.0.0',
            'flake8>=3.9.0',
            'mypy>=0.910'
        ],
        'test': [
            'pytest>=6.2.0',
            'pytest-cov>=2.12.0'
        ],
        'docs': [
            'sphinx>=4.0.0',
            'sphinx-rtd-theme>=0.5.0'
        ],
        'cloud': [
            'boto3>=1.18.0',
            'google-cloud-storage>=2.0.0',
            'azure-storage-blob>=12.9.0'
        ],
        'ml': [
            'scikit-learn>=1.0.0',
            'transformers>=4.12.0',
            'torch>=1.9.0'
        ]
    },
    
    # Entry points for command line tools
    entry_points={
        'console_scripts': [
            'pashto-pipeline=pashto_dataset.pipeline.main:main',
            'pashto-pipeline-test=pashto_dataset.pipeline.testing:main',
            'pashto-pipeline-scheduler=pashto_dataset.pipeline.scheduler:main',
        ]
    },
    
    # Python version requirement
    python_requires=">=3.7",
    
    # Package classification
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Text Processing :: Linguistic",
        "Topic :: System :: Archiving",
    ],
    
    # Keywords for package discovery
    keywords=[
        "pashto",
        "dataset",
        "pipeline",
        "orchestration",
        "data-processing",
        "machine-learning",
        "nlp",
        "text-processing",
        "automation"
    ],
    
    # Project URLs
    project_urls={
        "Bug Reports": "https://github.com/pashto-dataset/pipeline/issues",
        "Source": "https://github.com/pashto-dataset/pipeline",
        "Documentation": "https://pashto-dataset-pipeline.readthedocs.io/",
    },
    
    # Include data files
    include_package_data=True,
    package_data={
        'pashto_dataset': [
            'pipeline/README.md',
            'pipeline/requirements.txt',
            '**/*.json',
            '**/*.yaml',
            '**/*.yml',
        ]
    },
    
    # Exclude certain files from distribution
    zip_safe=False,
)