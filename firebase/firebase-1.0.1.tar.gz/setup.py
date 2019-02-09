"""
jt_calc Python package is a python interface to the Google's Firebase REST APIs
By Joe Tilsed
---
setup.py is the build script for setuptools.
It tells setuptools about your package (such as the name and version) as well as which code files to include.
"""

import setuptools

with open('README.md', 'r') as readme:
    long_description = readme.read()

setuptools.setup(
    name='firebase',
    version="1.0.1",
    author="Joe Tilsed",
    author_email="Joe@Tilsed.com",
    description="Python interface to the Google's Firebase REST APIs",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://bitbucket.org/joetilsed/firebase/",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3.7",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent"
    ]
)


# That's all folks...
