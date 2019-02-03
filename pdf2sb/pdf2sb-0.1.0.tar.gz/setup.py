# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['pdf2sb']

package_data = \
{'': ['*']}

install_requires = \
['pdf2image>=1.4,<2.0', 'pillow>=5.4,<6.0', 'python-gyazo>=1.1,<2.0']

entry_points = \
{'console_scripts': ['pdf2sb = pdf2sb:main']}

setup_kwargs = {
    'name': 'pdf2sb',
    'version': '0.1.0',
    'description': '',
    'long_description': '# pdf2sb\n',
    'author': 'reiyw',
    'author_email': 'reiyw.setuve@gmail.com',
    'url': 'https://github.com/reiyw/pdf2sb',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
