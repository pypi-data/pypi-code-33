#! /usr/local/bin/python3
from setuptools import setup

setup(
      name='find-macho-linkmap',
      version='1.0.0',
      description='find_macho_linkmap_and_output_otool_sections',
      author='LiTing',
      author_email='match.lt@alibaba-inc.com',
      license='MIT',
      classifiers=[
                   'Programming Language :: Python :: 3',
                   'License :: OSI Approved :: MIT License',
                   'Operating System :: OS Independent',
                   ],
      keywords='linkmap macho python',
      packages=['src', 'src.utils'],
      )
