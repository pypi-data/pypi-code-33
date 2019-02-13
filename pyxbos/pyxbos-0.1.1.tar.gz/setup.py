# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['pyxbos']

package_data = \
{'': ['*'], 'pyxbos': ['drivers/*', 'wave/*', 'wavemq/*']}

install_requires = \
['googleapis-common-protos>=1.5,<2.0',
 'grpcio-tools>=1.18,<2.0',
 'grpcio>=1.18,<2.0']

setup_kwargs = {
    'name': 'pyxbos',
    'version': '0.1.1',
    'description': 'Python bindings for XBOS-flavored WAVEMQ and related services',
    'long_description': None,
    'author': 'Gabe Fierro',
    'author_email': 'gtfierro@cs.berkeley.edu',
    'url': 'https://pypi.org/project/pyxbos',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.5,<4.0',
}


setup(**setup_kwargs)
