import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="pypaint",
    version="0.1",
    author="Erik Båvenstrand",
    author_email="erik.bavenstrands@gmail.com",
    description="Drawing module for python",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/ErikBavenstrand/pypaint",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    install_requires=['turtle'],
)