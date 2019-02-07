# -*- coding: utf-8 -*-
"""Installer for the collective.tiles.sliders package."""
from setuptools import find_packages
from setuptools import setup

setup(
    name='collective.tiles.sliders',
    version='1.0.0',
    description='A collection of slider tiles for Mosaic.',
    long_description='\n\n'.join([
        open('README.rst').read(),
        open('CONTRIBUTORS.rst').read(),
        open('CHANGES.rst').read(),
    ]),
    # Get more from https://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Framework :: Plone',
        'Framework :: Plone :: 5.1',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU General Public License v2 (GPLv2)',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
    ],
    keywords='Python Plone',
    author='it-spirit',
    author_email='development@it-spir.it',
    url='https://github.com/it-spirit/collective.tiles.sliders',
    download_url='https://pypi.python.org/pypi/collective.tiles.sliders',
    license='GPL version 2',
    packages=find_packages('src', exclude=['ez_setup']),
    namespace_packages=['collective', 'collective.tiles'],
    package_dir={'': 'src'},
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        'setuptools',
        'Products.GenericSetup>=1.8.2',
        'plone.api',
        'plone.app.tiles',
        'plone.tiles',
    ],
    extras_require={
        'mosaic': [
            'plone.app.mosaic',
        ],
        'test': [
            'plone.app.testing',
            'plone.testing',
            'plone.app.robotframework[debug]',
            'robotframework-selenium2screenshots',
            'plone.app.mosaic',
        ],
    },
    entry_points="""
    [z3c.autoinclude.plugin]
    target = plone
    """,
)
