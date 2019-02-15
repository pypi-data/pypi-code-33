# -*- coding: utf-8 -*-
"""
Created on Sun Jan 20 18:46:45 2019

@author: stasb
"""

import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="orbipy",
    version="0.1.5",
    author="Bober S.A.",
    author_email="stas.bober@gmail.com",
    description="Extensive orbital dynamics research tool for CRTBP and beyond",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://bitbucket.org/stas_bober/orbipy",
    packages=setuptools.find_packages(),
    package_data={
            'orbipy': ['data/*.csv'],
    },
    license='MIT',
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    install_requires=['numpy>=1.15.2', 
                      'scipy>=1.1.0',
                      'pandas>=0.23.4',
                      'matplotlib>=3.0.0',
                      'numba>=0.39.0',
                      ],
    python_requires='>=3.6',
)