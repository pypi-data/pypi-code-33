# (c) 2014 Mind Candy Ltd. All Rights Reserved.
# Licensed under the MIT License; you may not use this file except in compliance with the License.
# You may obtain a copy of the License at http://opensource.org/licenses/MIT.

from setuptools import setup, find_packages
from os import path
import sys


sys.path.insert(0, path.join(path.dirname(__file__), 'src'))
try:
    import fattoush
except ImportError:
    class fattoush:
        """ Placeholder for tox """

        VERSION = "Placeholder for tox"


setup(
    name='Fattoush',
    package_data={'': ['*.txt']},
    author='Alistair Broomhead',
    version=str(fattoush.VERSION),
    author_email='alistair.broomhead+python@gmail.com',
    description="A delicious testing framework",
    license='MIT',
    url='https://github.com/alistair-broomhead/fattoush',
    long_description=fattoush.__doc__,
    packages=find_packages('src'),
    package_dir={'': 'src'},
    install_requires=[
        "argparse>=1.2.1",
        "future",
        "jsonschema>=2.3.0",
        "lettuce==0.2.19",
        "packaging",
        "selenium>=3.0.0",
    ],
    extras_require={
        "fast": [
            "python-Levenshtein",
        ]
    },
    include_package_data=True,
    entry_points={
        'console_scripts': [
            'fattoush = fattoush.runner.bin:console']
    }
)
