import os
from codecs import open

from setuptools import setup, find_packages


BASE_DIR = os.path.abspath(os.path.dirname(__file__))
VERSION = __import__('cms_helpers').__version__


with open(os.path.join(BASE_DIR, 'README.rst'), encoding='utf-8') as f:
    long_description = f.read()


setup(
    name='django-cms-helpers',
    version=VERSION,
    description='django-cms-helpers is a collection of helpers when working with django-cms.',
    long_description=long_description,
    url='https://github.com/moccu/django-cms-helpers',
    project_urls={
        'Bug Reports': 'https://github.com/moccu/django-cms-helpers/issues',
        'Source': 'https://github.com/moccu/django-cms-helpers',
    },
    author='moccu',
    author_email='info@moccu.com',
    packages=find_packages(exclude=['tests', 'tests.*']),
    install_requires=['django-cms'],
    include_package_data=True,
    keywords='django',
    classifiers=[
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
    ],
)
