# -*- coding: utf-8 -*-

from setuptools import setup, find_packages

long_desc = '''
This package contains the youtube Sphinx extension.

The extension defines a directive, "youtube", for embedding YouTube
videos.
'''

requires = ['Sphinx>=0.6']

setup(
    name='sphinxembeddedvideos',
    version='1.0.0',
    url='https://github.com/Peque/sphinxembeddedvideos',
    download_url='https://pypi.org/project/sphinxembeddedvideos',
    license='BSD',
    author='Chris Pickel',
    author_email='sfiera@gmail.com',
    description='Sphinx extension to embed Youtube videos.',
    long_description=long_desc,
    zip_safe=False,
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Documentation',
        'Topic :: Utilities',
    ],
    platforms='any',
    packages=find_packages(),
    include_package_data=True,
    install_requires=requires,
)
