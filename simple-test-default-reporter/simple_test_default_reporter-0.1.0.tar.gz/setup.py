# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['simple_test_default_reporter',
 'simple_test_default_reporter.fns',
 'simple_test_default_reporter.fns.decorators',
 'simple_test_default_reporter.fns.internal',
 'simple_test_default_reporter.report',
 'simple_test_default_reporter.report.initRootState']

package_data = \
{'': ['*']}

install_requires = \
['ordered_set>=3.1,<4.0',
 'simple_chalk>=0.1.0,<0.2.0',
 'tedent>=0.1.1,<0.2.0',
 'wrapt>=1.10,<2.0']

setup_kwargs = {
    'name': 'simple-test-default-reporter',
    'version': '0.1.0',
    'description': 'The default reporter for simple_test',
    'long_description': 'I will document this module if people will find it helpful.  Currently\nsimple_test is just for my own personal use.\n',
    'author': 'Philip Olson',
    'author_email': 'philip.olson@pm.me',
    'url': 'https://github.com/olsonpm/py_simple-test-default-reporter',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
