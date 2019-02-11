#!/usr/bin/env python3

from setuptools import setup
import lethe

with open('README.md', 'r') as f:
    long_description = f.read()

setup(name='lethe',
      version=lethe.version,
      description='Git-based snapshotting',
      long_description=long_description,
      long_description_content_type='text/markdown',
      author='Jan Petykiewicz',
      author_email='anewusername@gmail.com',
      py_modules=['lethe'],
      entry_points={
          'console_scripts': [
              'lethe=lethe:main',
          ],
      },
      install_requires=[
            'typing',
      ],
      url='https://mpxd.net/code/jan/lethe',
      keywords=[
            'git',
            'snapshot',
            'commit',
            'refs',
            'backup',
            'undo',
            'log',
            'lab notebook',
            'traceability',
      ],
      classifiers=[
            'Programming Language :: Python',
            'Programming Language :: Python :: 3',
            'Development Status :: 4 - Beta',
            'Environment :: Other Environment',
            'Intended Audience :: Developers',
            'Intended Audience :: Science/Research',
            'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
            'Topic :: Software Development :: Version Control :: Git',
            'Topic :: Utilities',
      ],
      )
