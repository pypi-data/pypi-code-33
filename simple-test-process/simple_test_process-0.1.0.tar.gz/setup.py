# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['simple_test_process',
 'simple_test_process.fns',
 'simple_test_process.fns.decorators',
 'simple_test_process.fns.internal']

package_data = \
{'': ['*']}

install_requires = \
['case_conversion>=2.1,<3.0',
 'num2words>=0.5.8,<0.6.0',
 'ordered_set>=3.1,<4.0',
 'simple_chalk>=0.1.0,<0.2.0',
 'tedent>=0.1.1,<0.2.0',
 'toml>=0.10.0,<0.11.0',
 'wrapt>=1.10,<2.0']

setup_kwargs = {
    'name': 'simple-test-process',
    'version': '0.1.0',
    'description': 'The process ran by simple_test to isolate the environment',
    'long_description': 'I will document this module if people will find it helpful.  Currently\nsimple_test is just for my own personal use.\n',
    'author': 'Philip Olson',
    'author_email': 'philip.olson@pm.me',
    'url': 'https://github.com/olsonpm/py_simple-test-process',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
