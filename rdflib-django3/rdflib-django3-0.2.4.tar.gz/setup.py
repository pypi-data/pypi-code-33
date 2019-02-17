#! /usr/bin/env python3
import os
from setuptools import setup, find_packages


def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()


VERSIONING = {
    'root': '.',
    'version_scheme': 'guess-next-dev',
    'local_scheme': 'dirty-tag',
}


setup(
    name="rdflib-django3",
    use_scm_version=VERSIONING,
    setup_requires=['setuptools_scm'],
    url="http://github.com/devkral/rdflib-django3",
    license='MIT',
    description="Store implementation for RDFlib using Django models as its backend (fork)",  # noqa
    long_description=read('README.rst'),
    keywords='django rdf rdflib store',
    author='Alexander K., Yigal Duppen',
    author_email='devkral@web.de, yigal@publysher.nl',
    packages=find_packages(exclude=["test"]),
    zip_safe=True,
    install_requires=['rdflib>=3.2.1'],
    entry_points={
        'rdf.plugins.store': [
            'Django = rdflib_django.store:DjangoStore',
        ],
    },

    classifiers=[
        'Development Status :: 3 - Alpha',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
)
