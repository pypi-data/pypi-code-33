from setuptools import setup, find_packages

setup(
    name='ml4k',
    version='0.5',
    packages=find_packages(),
    install_requires=[
        'requests',
        'Pillow'
    ],
    long_description=open('README.md').read()
)
