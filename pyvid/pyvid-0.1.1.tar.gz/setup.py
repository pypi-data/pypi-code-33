# -*- coding: utf-8 -*-
from distutils.core import setup

modules = \
['pyvid']
install_requires = \
['click-spinner>=0.1.8,<0.2.0',
 'click>=7.0,<8.0',
 'colorama>=0.4.1,<0.5.0',
 'ffmpeg-python>=0.1.16,<0.2.0',
 'hurry.filesize>=0.9.0,<0.10.0']

entry_points = \
{'console_scripts': ['pyvid = pyvid:main']}

setup_kwargs = {
    'name': 'pyvid',
    'version': '0.1.1',
    'description': 'Video shrinker that uses ffmpeg.',
    'long_description': '# pyvid 0.1.1\n\n[![PyPI version](https://badge.fury.io/py/pyvid.svg)](https://badge.fury.io/py/pyvid)\n[![Build Status](https://travis-ci.org/0jdxt/pyvid.svg?branch=master)](https://travis-ci.org/0jdxt/pyvid)\n[![Documentation Status](https://readthedocs.org/projects/pyvid/badge/?version=latest)](https://pyvid.readthedocs.io/en/latest/?badge=latest)\n[![Coverage Status](https://coveralls.io/repos/github/0jdxt/pyvid/badge.svg?branch=master)](https://coveralls.io/github/0jdxt/pyvid?branch=master)\n\n\nPyvid is a package that shrinks video files using defaults on ffmpeg to get high quality and low file size. Works best on 1080p videos.\n\n## Dependencies\n\n- [install](https://www.ffmpeg.org/download.html)\n  ffmpeg with libx264 or libx265 support and make sure the executable is in $PATH\n\n## Installation\n\nInstall as global executable\n\n```\npip install --user pyvid\n```\n\n## Usage\n\nThe most basic usage is as follows:\n\n```\npyvid PATH\n```\n\nwhere PATH is a file or directory. If PATH is a directory, it will look for video files. Converted videos are placed in a `converted/` subfolder.\n\nThe following\n\n```\npyvid files -e ext1,ext2\n```\n\nwill convert all `.ext1` and `.ext2` files in directory `files/` to output directory `files/converted/`.\n\n```\nUsage: pyvid [OPTIONS] PATH\n\n  Convert video(s) in specified path.\n\nOptions:\n  -e, --ext TEXT  Comma seperated list of file extension(s) to look for\n  -y, --force     A single count disables per-video prompts. A count of 2\n                  disables all prompts.\n  -d, --rem       Delete source video files\n  --version       Show the version and exit.\n  --help          Show this message and exit.\n```\n',
    'author': 'jdxt',
    'author_email': 'jytrn@protonmail.com',
    'url': 'https://github.com/0jdxt/pyvid',
    'py_modules': modules,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
