'''
Created on 9 Feb 2019

@author: bennypopp
'''

import setuptools
from idna import package_data

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="RandomShapelets",
    version="0.0.9",
    author="BennyPopp",
    author_email="author@example.com",
    description="A small package for time series classification",
    long_description=long_description,
    long_description_content_type="text/markdown",
    #url="https://github.com/DataPop/RandomShapeletClassifier",
    packages=['additional', 'models'],
    package_data = {'additional': ['*.py', '*.csv'], 
                    'models': ['*.py',]},
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
