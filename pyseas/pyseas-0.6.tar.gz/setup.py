from setuptools import setup, find_packages
import os

with open("README.md", "r") as f:
    long_description = f.read()

setup(
    name="pyseas",
    version="0.6",
    author="Søren Christian Aarup",
    author_email="sc@aarup.org",
    description="A Python wrapper for seas-nve API",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/scaarup/pyseas",
    install_requires=['requests>=2.0'],
    python_requires='>=3',
    packages=find_packages(),
    classifiers=(
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ),
)
