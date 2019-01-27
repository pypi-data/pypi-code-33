import os
from setuptools import setup, find_packages

import puradouga

with open(os.path.join(os.path.dirname(__file__), 'README.md')) as f:
    long_description = f.read().strip()

setup(
    name='puradouga',
    description='Uradouga Plugin System',

    url='https://git.widmer.me/project/multimedia/puradouga',
    long_description=long_description,
    long_description_content_type='text/markdown',
    version=puradouga.__versionstr__,
    author='Joel Widmer',
    author_email='joel@widmer.me',
    packages=find_packages(".", exclude=["test_puradouga", "test_puradouga.*"]),
    package_dir={'puradouga': './puradouga'},
    keywords=['plugins', 'anidouga', ],
    classifiers=[
        "Programming Language :: Python :: 3.7",
    ],
)
