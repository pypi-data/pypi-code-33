"""Setuptools configuration file."""

# mynotes builds indexes and converts to HTML a tree of notes written in
# Markdown.
# Copyright (C) 2018 Yorick Brunet <mynotes@yok.ch>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

from setuptools import setup, find_packages
from mynotes.constants import VERSION


def readme():
    """Read README and return it.

    :return: README file content
    :rtype: str
    """
    with open('README.rst', 'r') as fpr:
        return fpr.read()


setup(name='mynotes',
      version=VERSION,
      description='Build index and generate HTML for markdown notes',
      long_description=readme(),
      long_description_content_type='text/x-rst',
      url='https://gitlab.com/yorickbrunet/mynotes',
      author='Yorick Brunet',
      author_email='mynotes@yok.ch',
      license='GPL version 3 or later',
      packages=find_packages(),
      install_requires=[
          'py-gfm',
          'Pygments',
      ],
      entry_points={
          'console_scripts': [
              'mynotes-build=mynotes.cli:build_index',
              'mynotes-genhtml=mynotes.cli:generate_html',
              ],
      },
      classifiers=[
          'Development Status :: 5 - Production/Stable',
          'Environment :: Console',
          'Programming Language :: Python :: 3',
          'Programming Language :: Python :: 3.7',
          'Topic :: Utilities',
          'License :: OSI Approved :: GNU General Public License v3'
          ' or later (GPLv3+)',
      ],
      python_requires='>= 3.7',
      zip_safe=False,
      setup_requires=['pytest-runner'],
      tests_require=['pytest'],
      )

# Some help:
# https://pypi.org/pypi?%3Aaction=list_classifiers
# https://packaging.python.org/guides/making-a-pypi-friendly-readme/
