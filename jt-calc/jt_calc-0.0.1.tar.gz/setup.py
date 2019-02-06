"""
jt_calc Python package is a simple custom calculator in Python 3.7.
By Joe Tilsed
---
setup.py is the build script for setuptools.
It tells setuptools about your package (such as the name and version) as well as which code files to include.
"""

import setuptools

with open('README.md', 'r') as readme:
    long_description = readme.read()

setuptools.setup(
    name='jt_calc',
    version="0.0.1",
    author="Joe Tilsed",
    author_email="Joe@Tilsed.com",
    description="Custom calculator in Python 3.7",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://bitbucket.org/tilsedtowers/jt_calc/src",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3.7",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent"
    ]
)


# That's all folks...
