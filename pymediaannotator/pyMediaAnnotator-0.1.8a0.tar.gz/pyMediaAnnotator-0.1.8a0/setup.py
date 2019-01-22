#!/bin/env python

from setuptools import setup
from setuptools import find_packages

with open("README.md", "r") as readme:
    long_description = readme.read()

setup(name='pyMediaAnnotator',
      version='0.1.8a',
      description='A pyGTK and vlc based application to hand-annotate audio '
                  'and video files for classification tasks',
      long_description=long_description,
      long_description_content_type="text/markdown",
      url='https://gitlab.com/aalok-sathe/pyMediaAnnotator.git',
      author='Aalok Sathe',
      author_email='aalok.sathe@richmond.edu',
      license='GPL-3',
      # packages=find_packages(),
      scripts=['pyMediaAnnotator'],
      python_requires='>=3.5',
      install_requires=['pyyaml>=3.12',
                        'python-vlc>=3.0.4106',
                        # 'pyGTK>=2.24.0',
                        'pyGGI>=1.1.3'],
      classifiers=[
          'Development Status :: 1 - Planning',
          'Intended Audience :: Developers',
          'Intended Audience :: Education',
          'Intended Audience :: Science/Research',
          'License :: OSI Approved :: GNU General Public License v3 '
                                      'or later (GPLv3+)',
          'Programming Language :: Python :: 3.6',
          'Topic :: Software Development :: Libraries :: Python Modules'],)
