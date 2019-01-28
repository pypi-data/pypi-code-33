# -*- coding: utf-8 -*-
from distutils.core import setup

modules = \
['speiseplan']
install_requires = \
['selenium-requests-html>=1.0,<2.0']

entry_points = \
{'console_scripts': ['speiseplan = speiseplan:main']}

setup_kwargs = {
    'name': 'speiseplan',
    'version': '0.1.1',
    'description': '',
    'long_description': None,
    'author': 'Markus Quade',
    'author_email': 'info@markusqua.de',
    'url': None,
    'py_modules': modules,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
