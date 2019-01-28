"""
Flask-Textile
-------------

A module for parsing Textile from within Flask applications.

Built on top of the Python port of Dean Allen's Textile, a humane web text generator.

https://github.com/textile/python-textile
https://www.textile-lang.com
https://en.wikipedia.org/wiki/Textile_(markup_language)
"""
from setuptools import setup

with open('README.md', 'r') as file:
    long_description = file.read()

setup(
    name='Flask-Textile',
    version='0.4.1.post1',
    url='https://git.sr.ht/~ethet/flask-textile',
    license='BSD',
    author='ethet',
    author_email='eth@ethet.org',
    description='Textile parsing from within Flask',
    long_description=long_description,
    long_description_content_type="text/markdown",
    py_modules=['flask_textile'],
    zip_safe=False,
    include_package_data=True,
    platforms='any',
    install_requires=[
        'Flask',
        'textile'
    ],
    classifiers=[
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Framework :: Flask',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ]
)
