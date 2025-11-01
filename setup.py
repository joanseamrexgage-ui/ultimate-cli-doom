#!/usr/bin/env python3
"""
Ultimate CLI DOOM - Setup Script
Production-grade installation and packaging
"""

import os
from setuptools import setup, find_packages

# Read README for long description
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

# Read requirements
with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

# Read dev requirements
with open("requirements-dev.txt", "r", encoding="utf-8") as fh:
    dev_requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="ultimate-cli-doom",
    version="1.0.0",
    author="Ultimate Coder & Claude",
    author_email="ultimate@coder.dev",
    description="The most advanced ASCII raycasting game ever built for command line",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/joanseamrexgage-ui/ultimate-cli-doom",
    project_urls={
        "Bug Tracker": "https://github.com/joanseamrexgage-ui/ultimate-cli-doom/issues",
        "Documentation": "https://github.com/joanseamrexgage-ui/ultimate-cli-doom#readme",
        "Source Code": "https://github.com/joanseamrexgage-ui/ultimate-cli-doom",
    },
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: End Users/Desktop",
        "Topic :: Games/Entertainment :: First Person Shooters",
        "Topic :: Terminals",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Operating System :: OS Independent",
        "Environment :: Console",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    extras_require={
        "dev": dev_requirements,
        "test": ["pytest>=6.0", "pytest-cov>=2.0", "pytest-mock>=3.0"],
        "lint": ["black>=22.0", "flake8>=4.0", "mypy>=0.950"],
    },
    entry_points={
        "console_scripts": [
            "ultimate-cli-doom=main:main",
            "doom-cli=main:main",
        ],
    },
    include_package_data=True,
    package_data={
        "src": ["*.txt", "*.md"],
    },
    zip_safe=False,
    keywords="game doom raycasting ascii cli terminal 3d quantum ai",
    platforms=["any"],
)
