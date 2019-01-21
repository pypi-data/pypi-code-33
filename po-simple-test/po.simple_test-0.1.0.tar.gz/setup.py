# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['po',
 'po.simple_test',
 'po.simple_test.cli',
 'po.simple_test.fns',
 'po.simple_test.fns.decorators',
 'po.simple_test.fns.internal',
 'po.simple_test.run']

package_data = \
{'': ['*']}

install_requires = \
['ordered_set>=3.1,<4.0',
 'simple_test_default_reporter>=0.1.0,<0.2.0',
 'simple_test_process>=0.1.0,<0.2.0',
 'wrapt>=1.10,<2.0']

entry_points = \
{'console_scripts': ['simple-test = po.simple_test.script:main']}

setup_kwargs = {
    'name': 'po.simple-test',
    'version': '0.1.0',
    'description': 'A simple test runner',
    'long_description': 'I will document this module if people will find it helpful.  Currently\nsimple_test is just for my own personal use.\n',
    'author': 'Philip Olson',
    'author_email': 'philip.olson@pm.me',
    'url': 'https://github.com/olsonpm/py_simple-test',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
