# -*- coding: utf8

import pypandoc
from setuptools import setup

long_description = pypandoc.convert_file("README.md", "rst")

setup(
    name='renew',
    description='Creates reproducible repr of arbitrary classes with a nice layout.',
    version='0.2',
    author='Michał Kaczmarczyk',
    author_email='michal.s.kaczmarczyk@gmail.com',
    maintainer='Michał Kaczmarczyk',
    maintainer_email='michal.s.kaczmarczyk@gmail.com',
    license='MIT license',
    url='https://gitlab.com/kamichal/renew',
    long_description=long_description,
    long_description_content_type='text/x-rst; charset=UTF-8',
    packages=['renew'],
    requires=[],
    install_requires=[],
    keywords='',
    classifiers=[
        # https://pypi.org/pypi?%3Aaction=list_classifiers
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Topic :: Software Development',
        'Topic :: Software Development :: Code Generators',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Operating System :: OS Independent',
        'License :: OSI Approved :: MIT License',
    ],
)
