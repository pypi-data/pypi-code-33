import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="isidiot",
    version="0.0.2",
    author="Ryan Broman",
    description="Determines if somebody is an idiot",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/gabixdev/is-idiot",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
)