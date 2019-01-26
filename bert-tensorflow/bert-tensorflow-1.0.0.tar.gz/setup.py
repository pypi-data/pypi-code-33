"""Install BERT."""
from setuptools import find_packages
from setuptools import setup

setup(
    name='bert-tensorflow',
    version='1.0.0',
    description='BERT',
    author='Google Inc.',
    author_email='no-reply@google.com',
    url='https://github.com/google-research/bert',
    license='Apache 2.0',
    packages=find_packages(),
    install_requires=[
        'six',
    ],
    extras_require={
        'tensorflow': ['tensorflow>=1.12.0'],
        'tensorflow_gpu': ['tensorflow-gpu>=1.12.0'],
        'tensorflow-hub': ['tensorflow-hub>=0.1.1'],
    },
)
