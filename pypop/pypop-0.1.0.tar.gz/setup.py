from setuptools import setup, find_packages
version = '0.1.0'

setup(
    name='pypop',
    version=version,
    description="A python library to compose pop songs automatically.",
    keywords='music pops',
    author='Yuma Mihira',
    url='https://github.com/yuma-m/pypop',
    license='MIT',
    packages=find_packages(exclude=['test']),
    install_requires=[
        'attrs',
        'pychord',
    ]
)
