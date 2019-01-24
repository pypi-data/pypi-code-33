from setuptools import setup
from os import path

here = path.abspath(path.dirname(__file__))

with open(path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(name='unittest_additions',
    version='0.1.2',
    description='Additional features to extend python unittest and mock.',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/c0yote/unittest-additions',
    author='U.G. Wilson',
    author_email='ugwilson@gmail.com',
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Topic :: Software Development :: Testing',
        'Topic :: Software Development :: Testing :: Mocking',
        'Topic :: Software Development :: Testing :: Unit',
        'Programming Language :: Python :: 3.7',
    ],
    keywords='unittest mock',
    py_modules=['unittest_additions'],
    project_urls={
        'Bug Reports': 'https://github.com/c0yote/unittest-additions/issues',
        'Source': 'https://github.com/c0yote/unittest-additions',
    })
