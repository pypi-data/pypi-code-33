from setuptools import setup, find_packages
from os import path
from io import open

here = path.abspath(path.dirname(__file__))

with open(path.join(here, "README.md"), encoding="utf-8") as f:
    long_description = f.read()

setup(
    name="ioexplorer-dataloader",
    version="0.0.14",
    description="A CLI for ingesting data into the IOExplorer database.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Ryan Marren",
    author_email="rymarr@tuta.io",
    classifiers=["Development Status :: 3 - Alpha"],
    packages=find_packages(),
    install_requires=[
        "sqlalchemy",
        "pandas",
        "numpy",
        "tqdm",
        "pyyaml",
        "click",
        "PyInquirer",
        "toolz",
        "psycopg2-binary",
    ],
    entry_points={"console_scripts": ["iodl = ioexplorer_dataloader.cli:cli"]},
    include_package_data=True,
)
