#
# Copyright 2017 the original author or authors.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
"""A setuptools based setup module.
See:
https://packaging.python.org/en/latest/distributing.html
https://github.com/pypa/sampleproject
"""
# Always prefer setuptools over distutils
from setuptools import setup, find_packages
from os import path

# io.open is needed for projects that support Python 2.7
# It ensures open() defaults to text mode with universal newlines,
# and accepts an argument to specify the text encoding
# Python 3 only projects can skip this import
from io import open

here = path.abspath(path.dirname(__file__))

# Get the long description from the README file
with open(path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()


setup(
    name='pyvoltha',
    version='0.1.7',
    description='VOLTHA Python support libraries',
    author='Chip Boling',
    author_email='chip@bcsw.net',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://wiki.opencord.org/display/CORD/VOLTHA',

    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Libraries',
        'License :: OSI Approved :: Apache Software License',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
    ],
    packages=find_packages(exclude=['tests']),
    install_requires=[
        "argparse == 1.2.1",
        "arrow == 0.10.0",
        "bitstring == 3.1.5",
        "cmd2 == 0.7.0",
        "colorama == 0.3.9",
        "confluent-kafka == 0.11.5",
        "cython == 0.24.1",
        "decorator == 4.1.2",
        "docker-py == 1.10.6",
        "etcd3 == 0.7.0",
        "flake8 == 3.7.3",
        "fluent-logger == 0.6.0",
        "gevent == 1.4.0",
        "grpc == 0.3.post19",
        "grpcio == 1.3.5",
        "grpcio-tools == 1.3.5",
        "hash_ring == 1.3.1",
        "hexdump == 3.3",
        "jinja2 == 2.8",
        "jsonpatch == 1.16",
        "jsonschema == 2.6.0",
        "kafka_python == 1.3.5",
        "klein == 17.10.0",
        "kubernetes == 5.0.0",
        "netaddr == 0.7.19",
        "networkx == 2.0",
        "mock == 2.0.0",
        "nose == 1.3.7",
        "nose-exclude == 0.5.0",
        "nose-testconfig == 0.10",
        "netifaces == 0.10.6",
        "pcapy == 0.11.1",
        "pep8 == 1.7.1",
        "pep8-naming>=0.3.3",
        "protobuf == 3.3.0",
        "protobuf-to-dict == 0.1.0",
        "pyflakes == 2.1.0",
        "pylint == 1.9.4",
        "python-consul == 0.6.2",
        "pyOpenSSL == 17.3.0",
        "PyYAML == 3.12",
        "requests == 2.18.4",
        "scapy == 2.3.3",
        "service-identity == 17.0.0",
        "simplejson == 3.12.0",
        "six == 1.12.0",
        "structlog == 17.2.0",
        "termcolor == 1.1.0",
        "transitions == 0.6.4",
        "treq == 17.8.0",
        "Twisted == 17.9.0",
        "txaioetcd == 0.3.0",
        "urllib3 == 1.22",
        "afkak == 3.0.0.dev20181106",
    ],
    dependency_links=["git+https://github.com/ciena/afkak.git#egg=afkak-3.0.0.dev20181106"]
)
