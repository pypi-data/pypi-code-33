"""Setuptool to pack the module."""

from setuptools import setup, find_packages

with open("README.md", "r") as fh:
    LONG_DESCRIPTION = fh.read()

setup(
    name="metadata_expander",

    use_scm_version=True,
    setup_requires=['setuptools_scm'],
    install_requires=[
        "beautifulsoup4",
        "bibtexparser",
        "scraping_browser>=0.2.4",
    ],

    author="Fabian Pflug",
    author_email="pflug@chi.uni-hannover.de",
    description="doi search and return metadata",

    long_description=LONG_DESCRIPTION,
    long_description_content_type="text/markdown",

    url="https://gibraltar.chi.uni-hannover.de/literature/metadata_expander",

    packages=find_packages(".", exclude=["test"]),

    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
