#!/usr/bin/python

from setuptools import setup, find_packages
from pyquilted import __version__


with open('README.md', 'r') as f:
    readme = f.read()

setup(
        name='pyquilted',
        version=__version__,
        license='MIT',
        description='convert a yaml file to a pdf resume',
        long_description=readme,
        long_description_content_type='text/markdown',
        author='Hong Tuyen',
        author_email='hong@coroutine.co',
        url='https://github.com/cocoroutine/pyquilted',
        keywords='quilted resume',
        packages=find_packages(),
        package_data={
            'pyquilted': ['templates/*.mustache', 'sample/*.yml']
            },
        include_package_data=True,
        install_requires=[
            'chevron',
            'pdfkit',
            'ruamel.yaml<=0.15.37',
            ],
        entry_points={
            'console_scripts':['pyquilted=pyquilted.main:main']
            },
        classifiers=[
            'Development Status :: 4 - Beta',
            'License :: OSI Approved :: MIT License',
            'Programming Language :: Python :: 3.5',
            'Programming Language :: Python :: 3.6',
            'Programming Language :: Python :: 3.7',
            ]
        )
