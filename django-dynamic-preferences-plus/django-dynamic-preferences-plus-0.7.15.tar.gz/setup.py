# !/usr/bin/env python
# encoding:UTF-8

import os
from setuptools import setup, find_packages
import dynamic_preferences

README = open(os.path.join(os.path.dirname(__file__), 'README.md')).read()
VERSION = dynamic_preferences.__version__

# allow setup.py to be run from any path
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

setup(
    name='django-dynamic-preferences-plus',
    packages=find_packages(),
    version=VERSION,
    description='A django app for registering dynamic global, site and user preferences',
    long_description=README,
    author='Team QWL',
    author_email='padova@quag.com',
    url='https://github.com/mirk8xr/django-dynamic-preferences',
    download_url='https://github.com/mirk8xr/django-dynamic-preferences/archive/%s.tar.gz' % VERSION,
    include_package_data=True,
    license='BSD',
    zip_safe=False,
    keywords=['django', 'preferences', 'admin'],
    classifiers=[
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
    ],
    install_requires=[
        "django<1.7",
        "six",
    ],
)
