""" Setup configuration fo pypi
"""
from setuptools import setup
setup(
    name='mbwebapppy',
    version='0.1.9',
    packages=['mbwebapppy'],
    include_package_data=True,
    python_requires='>=3',
    license='MIT License',
    description='A library to work with Mercedes WebApp API.',
    long_description='A library to work with Mercedes WebApp API.',
    author='Rene Nulsch',
    author_email='github.mbwebapppy@nulsch.de',
    classifiers=[
        'Intended Audience :: Developers',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Topic :: Internet',
    ],
    install_requires=[
        'requests>=2.18.4',
        'lxml>=4.2.0'
    ]
)