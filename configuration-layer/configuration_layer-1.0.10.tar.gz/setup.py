import setuptools
from setuptools import setup, find_packages
# To use a consistent encoding
from codecs import open
from os import path

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name='configuration_layer',
    version='1.0.10',
    packages=find_packages(exclude=['contrib', 'docs', 'tests*']),
    python_requires='~=3.6',
    url='',
    license='MIT',
    author='Antonio Di Mariano',
    author_email='antonio.dimariano@gmail.com',
    description='Initial configuration layer for microservices',
    long_description=long_description,
    long_description_content_type="text/markdown",
    install_requires=['avro-python3', 'confluent-kafka', 'kafka',
                      'requests',
                      'microservices_messaging_layer',
                      'fastavro'],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.6'
    ],
)