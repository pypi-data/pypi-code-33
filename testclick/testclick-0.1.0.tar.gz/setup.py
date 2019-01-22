# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['testclick']

package_data = \
{'': ['*']}

install_requires = \
['click>=7.0,<8.0']

entry_points = \
{'console_scripts': ['helloworld2 = testclick:helloworld.hello',
                     'helloworld3 = testclick:helloworld.hello2']}

setup_kwargs = {
    'name': 'testclick',
    'version': '0.1.0',
    'description': '',
    'long_description': None,
    'author': 'saiteja',
    'author_email': 'saitejapakalapati.a4@gmail.com',
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=2.7,<3.0',
}


setup(**setup_kwargs)
