"""Setup module to pack the code for PyPi."""

from setuptools import setup, find_packages

with open("README.md", "r") as fh:
    LONG_DESCRIPTION = fh.read()

setup(
    name="scraping_browser",

    use_scm_version=True,
    setup_requires=['setuptools_scm'],

    install_requires=['requests'],

    author="Fabian Pflug",
    author_email="pflug@chi.uni-hannover.de",
    description="Web-Scraping browser emulator",

    long_description=LONG_DESCRIPTION,
    long_description_content_type="text/markdown",

    url="https://gibraltar.chi.uni-hannover.de/pflug/browser",

    packages=find_packages(".", exclude=["tests"]),

    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
