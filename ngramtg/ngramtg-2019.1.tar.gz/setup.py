import setuptools
import ngramtg

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name=ngramtg.name,
    version=ngramtg.version,
    author=ngramtg.author,
    author_email="paulwicking@gmail.com",
    description="A simple ngram-based random text generator.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/docwicking/ngramtg",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
