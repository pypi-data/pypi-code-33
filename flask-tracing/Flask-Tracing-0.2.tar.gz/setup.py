"""
Flask-Tracing
-------------

Tracing utilities for flask application.
"""
from setuptools import setup

setup(
    name='Flask-Tracing',
    version='0.2',
    url='https://github.com/Handsome2734/Flask-Tracing',
    license='BSD',
    author='Handsome2734',
    author_email='songbowen1229@gmail.com',
    description='Tracing utilities for your flask application.',
    long_description=__doc__,
    py_modules=['flask_tracing'],
    zip_safe=False,
    include_package_data=True,
    platforms='any',
    install_requires=[
        'Flask'
    ],
    classifiers=[
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ]
)
