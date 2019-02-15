import re
import io
from setuptools import setup, find_packages

__version__ = re.search(
    r'__version__\s*=\s*[\'"]([^\'"]*)[\'"]',  # It excludes inline comment too
    io.open('empatican/__init__.py', encoding='utf_8_sig').read()).group(1)

long_description = '''Empatican provides utility methods for handling physio
archives in zip archive, hdf5 and unzipped directory structures, and has methods
to efficiently convert sparse physio timestamps and frequency metadata to dense
datetime indices.

It also provides a ``empatican`` download command-line utility to download and
organize physio zips from the *Empatica Connect* website. '''

setup(
    name='empatican',
    version=__version__,
    description='Empatica Physio Utilities',
    url='http://github.com/kastman/empatican',
    author='Erik Kastman',
    author_email='erik.kastman@gmail.com',
    packages=find_packages(),
    classifiers=[
        'Development Status :: 3 - Alpha',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',
        'Topic :: Utilities',
    ],
    entry_points={
        'console_scripts': ['empatican=empatican.cli:main'],
    },
    license='MIT',
    long_description=long_description,
    install_requires=['pandas', 'requests', 'tqdm'],
    test_suite='nose.collector',
    tests_require=['nose'],
    zip_safe=True)
