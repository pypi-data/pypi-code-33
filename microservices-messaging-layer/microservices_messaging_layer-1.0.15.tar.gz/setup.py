import setuptools
from setuptools import setup, find_packages
# To use a consistent encoding
from codecs import open
from os import path

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name='microservices_messaging_layer',
    version='1.0.15',
    packages=find_packages(exclude=['contrib', 'docs', 'tests*']),
    install_requires=['avro-python3', 'kafka', 'requests', 'confluent-kafka'],
    url='',
    license='',
    python_requires='~=3.6',
    author='Antonio Di Mariano',
    author_email='antonio.dimariano@gmail.com',
    description='Messaging Communication Layer for Microservices Architecture',
    long_description=long_description,
    long_description_content_type="text/markdown",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ]
)
