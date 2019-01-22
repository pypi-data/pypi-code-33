# encoding=utf-8
# date: 2019/1/22
__author__ = "Masako"

from distutils.core import setup

setup(
    name='Elise',
    version='0.1.4',
    author='Masako',
    author_email='Masako@example.com',
    url='https://github.com/TitledPythonFile',
    license='GPL',
    description='Simple multithreading spider',
    long_description=open('README.txt').read(),
    install_requires=[
        "requests==2.19.1",
    ],
)