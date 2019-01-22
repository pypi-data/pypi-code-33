#!/usr/bin/env python

"""
distutils/setuptools install script.
"""
import os
import re
import codecs

from setuptools import setup, find_packages


ROOT = os.path.dirname(__file__)
VERSION_RE = re.compile(r'''__version__ = ['"]([0-9.]+)['"]''')


def get_version():
    init = open(os.path.join(ROOT, 'imagekitio', '__init__.py')).read()
    return VERSION_RE.search(init).group(1)

# with open('LICENSE.txt') as f:
#     license = f.read()


# Get the long description from the relevant file
try:
    f = codecs.open('README.rst', encoding='utf-8')
    readme = f.read()
    f.close()
except:
    long_description = ''

setup(
    name='imagekitio',
    author_email='developer@imagekit.io',
    version=get_version(),
    description='imagekit Python SDK',
    long_description=readme,
    author='imagekit-developer',
    url='http://imagekit.io',
    license='MIT',
    keywords="imagekit image upload transform",
    packages=find_packages(exclude=['examples', 'tests']),
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        'Natural Language :: English',
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
        "Topic :: Internet :: WWW/HTTP",
    ],
    include_package_data=True,
    zip_safe=False,
    test_suite="tests"
    )

