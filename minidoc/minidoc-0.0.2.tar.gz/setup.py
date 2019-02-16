#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""The setup script."""

from setuptools import setup, find_packages

try:
    with open('./README.rst') as readme_file:
        readme = readme_file.read()
except:
    readme = "refer to https://github.com/ihgazni2/minidoc/"
else:
    pass

requirements = [
    "termtosvg",
    "elist",
    "efdir",
    "estring"
]

setup_requirements = [
    "termtosvg",
    "elist",
    "efdir",
    "estring"
]


setup(
    name='minidoc',
    version='0.0.2',
    description="auto generate a mini rst doc (code block + svg) from a test-file",
    long_description=readme,
    author="dli",
    author_email='286264978@qq.com',
    url='https://github.com/ihgazni2/minidoc',
    packages=find_packages(),
    package_data={
                  'documentation': ['docs/*']
                 },
    include_package_data=True,
    install_requires=requirements,
    license="MIT license",
    keywords='doc,test,svg',
     entry_points = {
         'console_scripts': ['minidoc=minidoc.bin:main']
    },
    classifiers=[
        'Environment :: Console',
        'Environment :: Web Environment',
        'Intended Audience :: End Users/Desktop',
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
    ],
    setup_requires=setup_requirements,
    py_modules=['minidoc'],
)
