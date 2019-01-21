"""Setup module, used for packaging time_converter to make it installable with pip
based on: https://github.com/pypa/sampleproject/blob/master/setup.py
"""

from setuptools import setup, find_packages

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name='time_converter',

    version='1.0.0',

    description='A Python class that allows for convenient conversion between different date and time formats/units',
    long_description=long_description,
    long_description_content_type="text/markdown",
    url='https://gitlab.physik.uni-kiel.de/ET/time_converter',
    author='Johan von Forstner',
    author_email='forstner@physik.uni-kiel.de',

    packages=find_packages(),
    install_requires=['numpy'],
    extras_require={
        'dev': ['pytest', 'pytest-cov', 'numpydoc', 'Sphinx'],
    },
    package_data={
        'time_converter.converters.': ['version.txt', 'sclk/msl.tsc'],
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
