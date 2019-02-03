import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="setbitcounter_pkg",
    version="1.0",
    author="Diksha Rawat",
    author_email="diksharawat1410@gmail.com",
    description="A package to count set bits of continous natural numbers in a  range",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/diksha-rawat/SetBitCount",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
