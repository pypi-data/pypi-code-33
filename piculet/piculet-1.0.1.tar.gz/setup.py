# -*- coding: utf-8 -*-
from distutils.core import setup

modules = \
['piculet']
extras_require = \
{'yaml': ['pyyaml>=3.13,<4.0']}

entry_points = \
{'console_scripts': ['piculet = piculet:main']}

setup_kwargs = {
    'name': 'piculet',
    'version': '1.0.1',
    'description': 'XML/HTML scraper using XPath queries.',
    'long_description': 'Copyright (C) 2014-2019 H. Turgut Uyar <uyar@tekir.org>\n\nPiculet is a module for extracting data from XML or HTML documents\nusing XPath queries. It consists of a `single source file`_\nwith no dependencies other than the standard library, which makes it very easy\nto integrate into applications. It also provides a command line interface.\n\n:PyPI: https://pypi.org/project/piculet/\n:Repository: https://github.com/uyar/piculet\n:Documentation: https://piculet.readthedocs.io/\n\nPiculet has been tested with Python 2.7, Python 3.4+, and compatible\nversions of PyPy. You can install the latest version using ``pip``::\n\n    pip install piculet\n\n.. _single source file: https://github.com/uyar/piculet/blob/master/piculet.py\n',
    'author': 'H. Turgut Uyar',
    'author_email': 'uyar@tekir.org',
    'url': 'https://github.com/uyar/piculet',
    'py_modules': modules,
    'extras_require': extras_require,
    'entry_points': entry_points,
    'python_requires': '>=2.7, !=3.0.*, !=3.1.*, !=3.2.*, !=3.3.*',
}


setup(**setup_kwargs)
