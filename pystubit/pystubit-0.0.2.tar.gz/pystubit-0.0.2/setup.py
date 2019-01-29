# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import unicode_literals
import os
from setuptools import setup
import sdist_upip

try:
    with open('README.rst') as f:
        readme = f.read()
except IOError:
    readme = ''

def _requires_from_file(filename):
    return open(filename).read().splitlines()

# version
here = os.path.dirname(os.path.abspath(__file__))
version = next((line.split('=')[1].strip().replace("'", '')
                for line in open(os.path.join(here,
                                              'pystubit',
                                              '__init__.py'))
                if line.startswith('__version__ = ')),
               '0.0.dev0')


def main():
    description = 'MicroPython library for StuduinoBit&ArtecRobo2.0'

    setup(
        name='pystubit',
        version='0.0.2',
        author='Artec Co., Ltd.',
        url='https://github.com/artec-kk/pystuduino',
        author_email='support@artec-kk.co.jp',
        maintainer='Artec Co., Ltd.',
        maintainer_email='support@artec-kk.co.jp',

        description=description,
        long_description=readme,
        zip_safe=False,
        include_package_data=True,
        install_requires=[],
        tests_require=[],
        setup_requires=[],
        entry_points="""
            # -*- Entry points: -*-
            [console_scripts]
            pkgdep = studuino.scripts.command:main
        """,
    )

if __name__ == '__main__':
    main()

