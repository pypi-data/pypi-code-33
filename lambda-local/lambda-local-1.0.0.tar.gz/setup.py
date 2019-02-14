import setuptools
from distutils.core import Extension

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="lambda-local",
    version="1.0.0",
    author="Abhimanyu HK",
    author_email="manyu1994@hotmail.com",
    description="A AWS Lambda Running In Local package.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/AbhimanyuHK/Lambda_Local",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 2",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
