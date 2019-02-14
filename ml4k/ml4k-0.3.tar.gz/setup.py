from setuptools import setup, find_packages

setup(
    name='ml4k',
    version='0.3',
    packages=find_packages(),
    install_requires=[
        'requests'
    ],
    long_description=open('README.md').read()
)
