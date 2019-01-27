from io import open
from os import path

from setuptools import find_packages, setup

here = path.abspath(path.dirname(__file__))

# Get the long description from the README file
with open(path.join(here, 'README.rst'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='django-controlcenter',
    version='0.2.9',
    description='Set of widgets to build dashboards for your Django-project.',
    long_description=long_description,
    url='https://github.com/byashimov/django-controlcenter',
    author='Murad Byashimov',
    author_email='byashimov@gmail.com',
    packages=find_packages(
        exclude=['controlcenter.stylus', 'controlcenter.images']),
    include_package_data=True,
    license='BSD',
    install_requires=['django-pkgconf'],
    keywords='django admin dashboard',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Environment :: Web Environment',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Framework :: Django',
        'Framework :: Django :: 1.8',
        'Framework :: Django :: 1.9',
        'Framework :: Django :: 1.10',
        'Framework :: Django :: 2.0',
    ],
)
