import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="sketcher",
    version="0.1.0",
    author="Théo (Lattay) Cavignac",
    author_email="theo.cavignac@gmail.com",
    description="A processing like sketch framework for prototyping.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/lattay/sketcher",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
