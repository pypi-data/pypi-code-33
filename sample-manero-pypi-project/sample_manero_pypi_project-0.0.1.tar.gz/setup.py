import os
from setuptools import setup, find_packages

setup(
    name = "sample_manero_pypi_project",
    version = "0.0.1",
    author = "Manero",
    url = "http://packages.python.org/sample_manero_pypi_project",
    author_email = "my.bin@live.com",
    description = ("Sample desc"),
    license = "BSD",
    keywords = "Sample",    
    packages=find_packages()
)