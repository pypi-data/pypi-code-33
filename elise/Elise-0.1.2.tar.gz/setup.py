# encoding=utf-8
# date: 2019/1/22
__author__ = "Masako"

from distutils.core import setup

setup(
    name='Elise',
    version='0.1.2',
    author='Masako',
    author_email='Masako@example.com',
    packages=['sdist'],
    url='https://github.com/TitledPythonFile/',
    license='GPL',
    description='Simple multithreading spider',
    long_description=open('README.md').read(),
    install_requires=[
        "requests==2.19.1",
    ],
)
