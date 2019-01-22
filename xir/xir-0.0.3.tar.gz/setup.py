#!/usr/bin/env python
# https://github.com/kennethreitz/setup.py/blob/master/setup.py
import os
import sys
import io
from setuptools import find_packages, setup

NAME = 'xir'
DESCRIPTION = 'Experiment Model Intermediate Representation'
URL = 'https://gitlab.com/mergetb/xir'
EMAIL = 'rgoodfel@isi.edu'
AUTHOR = 'Ryan Goodfellow'
REQUIRES_PYTHON = '>=3'
VERSION = None

# What packages are required for this module to be executed?
REQUIRED = [
    'ipython>=7.1.1',
    'PyYAML>=3.13',
]

# What packages are optional?
EXTRAS = {
    # 'fancy feature': ['django'],
}

# The rest you shouldn't have to touch too much :)
# ------------------------------------------------
# Except, perhaps the License and Trove Classifiers!
# If you do change the License, remember to change the Trove Classifier for that!

HERE = os.path.abspath(os.path.dirname(__file__))

# Import the README and use it as the long-description.
# Note: this will only work if 'README.md' is present in your MANIFEST.in file!
with io.open(os.path.join(HERE, 'README.md'), encoding='utf-8') as f:
    LDESCRIPTION = '\n' + f.read()

# Load the package's __version__.py module as a dictionary.
if not VERSION:
    with io.open(os.path.join(HERE, 'VERSION')) as f:
        VERSION = f.read()

# 'setup.py publish' shortcut.
if sys.argv[-1] == 'publish' or sys.argv[-1] == 'test':

    print('Deleting old distributions')
    os.system('rm %s/dist/*' % HERE)

    print('Building Source and Wheel')
    os.system('python setup.py sdist bdist_wheel')
    if sys.argv[-1] == 'test':
        os.system('twine upload --repository-url https://test.pypi.org/legacy/ dist/*')
    else:
        os.system('twine upload dist/*')
        print('Pushing git tags')
        os.system('git tag python-v{0}'.format(VERSION))
        os.system('git push --tags')
    sys.exit()

setup(
    name=NAME,
    version=VERSION,
    description=DESCRIPTION,
    author=AUTHOR,
    author_email=EMAIL,
    python_requires=REQUIRES_PYTHON,
    url=URL,
    long_description=LDESCRIPTION,
    long_description_content_type="text/markdown",
    license='Apache2.0',
    packages=find_packages(),
    install_requires=REQUIRED,
    include_package_data=True,
    zip_safe=False,
    classifiers=[
        "Programming Language :: Python :: 3",
        "Development Status :: 4 - Beta",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
    ],
)
