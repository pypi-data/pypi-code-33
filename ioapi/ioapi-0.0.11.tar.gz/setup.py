"""A Python GraphQL client for accessing the IOExplorer GraphQL API."""
import io
from setuptools import setup, find_packages

setup(
    name="ioapi",
    version="0.0.11",
    author="Ryan Marren",
    author_email="rymarr@tuta.io",
    packages=find_packages(exclude=["test*"]),
    license="MIT",
    description=("A Python client for accessing the IOExplorer API"),
    long_description=io.open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    install_requires=["quiz"],
    include_package_data=True,
)
