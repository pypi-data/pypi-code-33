# -*- coding: utf-8 -*-
from distutils.core import setup

package_dir = \
{'': 'src'}

packages = \
['dlc_gui']

package_data = \
{'': ['*'], 'dlc_gui': ['.hypothesis/unicodedata/11.0.0/*']}

install_requires = \
['PySide2==5.11.2',
 'numpy>=1.0.0,<2.0.0',
 'pandas>=0.24.0,<0.25.0',
 'ruamel.yaml>=0.15,<0.16',
 'tables>=3.4,<4.0']

setup_kwargs = {
    'name': 'dlc-gui',
    'version': '0.3.0',
    'description': 'Labeling GUI for DeepLabCut',
    'long_description': None,
    'author': 'd_',
    'author_email': 'UnicodeAlt255@gmail.com',
    'url': None,
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
