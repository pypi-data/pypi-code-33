from __future__ import print_function


from os.path import dirname, join
from setuptools import find_packages, setup


def read_description():
    with open(join(dirname(__file__), 'README.md')) as file:
        return file.read()


setup(
    name="quickplug",
    version="0.0.1",
    author="Christopher S. Fekete",
    author_email="cfekete93@hotmail.com",
    description=(
        "A general purpose plugin framework for rapid "
        "application development and extensibility."
    ),
    long_description=read_description(),
    long_description_content_type="text/markdown",
    url="https://github.com/cfekete93/quickplug",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Development Status :: 1 - Planning",
    ],
)
