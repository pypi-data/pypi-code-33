# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['cafe',
 'cafe.abc',
 'cafe.datastructs',
 'cafe.datastructs.units',
 'cafe.decorators',
 'cafe.logging',
 'cafe.patterns',
 'cafe.patterns.context',
 'cafe.twisted']

package_data = \
{'': ['*']}

install_requires = \
['PyYAML>=3.13,<4.0', 'six>=1.12,<2.0']

extras_require = \
{':python_version >= "2.7" and python_version < "2.8"': ['enum34>=1.1,<2.0']}

setup_kwargs = {
    'name': 'python-cafe',
    'version': '0.17.0',
    'description': 'Python Cafe: A convenience package providing various building blocks enabling pythonic patterns.',
    'long_description': '.. image:: https://badge.fury.io/py/python-cafe.svg\n    :target: https://badge.fury.io/py/python-cafe\n\nPython Cafe Package\n===================\n\nA convenience package providing various building blocks for pythonic patterns.\n',
    'author': 'Arun Babu Neelicattu',
    'author_email': 'arun.neelicattu@gmail.com',
    'url': 'https://github.com/abn/python-cafe',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'python_requires': '>=2.7, !=3.0.*, !=3.1.*, !=3.2.*, !=3.3.*',
}


setup(**setup_kwargs)
