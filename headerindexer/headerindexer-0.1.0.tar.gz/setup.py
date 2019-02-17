import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="headerindexer",
    version="0.1.0",
    author="Daniel Paz Avalos",
    author_email="dpazavalos@protonmail.com",
    description="A simple system to create a dictionary containing "
    "given keys to needed header column indexes",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/dpazavalos/Header-Indexer",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)