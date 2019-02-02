from setuptools import setup, find_packages

setup(
    name='ml4k',
    version='0.2',
    packages=find_packages(),
    install_requires=[
        'requests',
        'pillow'
    ],
    long_description=open('README.md').read()
)
