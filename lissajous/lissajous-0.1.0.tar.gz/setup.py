# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['lissajous']

package_data = \
{'': ['*']}

install_requires = \
['matplotlib>=3.0,<4.0', 'numpy>=1.16,<2.0']

entry_points = \
{'console_scripts': ['lissajous = lissajous.__main__:main']}

setup_kwargs = {
    'name': 'lissajous',
    'version': '0.1.0',
    'description': 'A Lissajous Curve Visualizer written in Python',
    'long_description': None,
    'author': 'kosayoda',
    'author_email': 'kieransiek@gmail.com',
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
