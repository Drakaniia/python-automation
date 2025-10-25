"""
setup.py
Package configuration for Python Automation System
"""
from setuptools import setup, find_packages
from pathlib import Path

# Read README for long description
readme_file = Path(__file__).parent / "README.md"
long_description = readme_file.read_text(encoding='utf-8') if readme_file.exists() else ""

setup(
    name="python-automation",
    version="1.0.0",
    author="Eyabnyez",
    author_email="alistairybaez574@gmail.com",
    description="A powerful CLI automation toolkit with AI-powered Git operations",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Drakaniia/python-automation",
    packages=find_packages(exclude=["tests", "tests.*", "backups", "backups.*"]),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Build Tools",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.7",
    install_requires=[
        # No external dependencies for core functionality
    ],
    extras_require={
        "test": [
            "pytest>=7.4.0",
            "pytest-cov>=4.1.0",
            "pytest-mock>=3.11.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "magic=automation.magic:main",
        ],
    },
    include_package_data=True,
    zip_safe=False,
)