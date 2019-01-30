from setuptools import setup, find_packages

setup(
    name = 'osimis_email_helpers',
    packages = find_packages(),
    version='0.1.2',  # always keep all zeroes version, it's updated by the CI script
    setup_requires=[],
    description = 'A simple library to make email sending easy.',
    author = 'Benoit Crickboom',
    author_email = 'bc@osimis.io',
    url = 'https://bitbucket.org/osimis/python-osimis-email-helpers',
    keywords = ['Helpers', 'Email'],
    classifiers = [],
)
