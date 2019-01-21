"""Setup file for Interkamen program."""
#!/usr/bin/env python3.7
# -*- coding: utf-8 -*-


import io
import os
import sys
from shutil import rmtree

from setuptools import find_packages, setup, Command

NAME = 'interkamen_career'
DESCRIPTION = 'Manage mining company.'
URL = 'https://github.com/Acetonen/Interkamen_career'
EMAIL = 'acetonen@gmail.com'
AUTHOR = 'Anton Kovalev'
REQUIRES_PYTHON = '>=3.7.0'
VERSION = None

REQUIRED = [
    'pandas', 'matplotlib', 'openpyxl', 'pillow', 'sentry-sdk', 'bcrypt'
]

EXTRAS = {}

HERE = os.path.abspath(os.path.dirname(__file__))

# Import the README and use it as the long-description.
try:
    with io.open(os.path.join(HERE, 'README.md'), encoding='utf-8') as file:
        LONG_DESCRIPTION = '\n' + file.read()
except FileNotFoundError:
    LONG_DESCRIPTION = DESCRIPTION

# Load the package's __version__.py module as a dictionary.
ABOUT = {}
if not VERSION:
    with open(os.path.join(HERE, NAME, '__version__.py')) as file:
        exec(file.read(), ABOUT)
else:
    ABOUT['__version__'] = VERSION


class UploadCommand(Command):
    """Support setup.py upload."""

    description = 'Build and publish the package.'
    user_options = []

    @staticmethod
    def status(status):
        """Prints things in bold."""
        print('\033[1m{0}\033[0m'.format(status))

    def initialize_options(self):
        """initialize."""
        pass

    def finalize_options(self):
        """finalize."""
        pass

    def run(self):
        """run upload."""
        try:
            self.status('Removing previous builds…')
            rmtree(os.path.join(HERE, 'dist'))
        except OSError:
            pass

        self.status('Building Source and Wheel (universal) distribution…')
        os.system('{0} setup.py sdist bdist_wheel --universal'.format(sys.executable))

        self.status('Uploading the package to PyPI via Twine…')
        os.system('twine upload dist/*')

        self.status('Pushing git tags…')
        os.system('git tag v{0}'.format(ABOUT['__version__']))
        os.system('git push --tags')

        sys.exit()


setup(
    name=NAME,
    version=ABOUT['__version__'],
    description=DESCRIPTION,
    long_description=LONG_DESCRIPTION,
    long_description_content_type='text/markdown',
    author=AUTHOR,
    author_email=EMAIL,
    python_requires=REQUIRES_PYTHON,
    url=URL,
    packages=find_packages(exclude=('dev_interkamen',)),
    install_requires=REQUIRED,
    extras_require=EXTRAS,
    include_package_data=True,
    scripts=['bin/interkamen'],
    license='MIT',
    classifiers=[
        'Environment :: Console',
        'Natural Language :: Russian',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: Implementation :: CPython',
    ],
    # $ setup.py publish support.
    cmdclass={
        'upload': UploadCommand,
    },
)
