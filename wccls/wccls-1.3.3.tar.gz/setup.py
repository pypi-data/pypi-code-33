# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['wccls']

package_data = \
{'': ['*']}

install_requires = \
['requests-html>=0.9.0,<0.10.0']

setup_kwargs = {
    'name': 'wccls',
    'version': '1.3.3',
    'description': 'Scraper for the WCCLS account page',
    'long_description': 'Overview\n========\nThis is a scraper for the WCCLS account page.\n\nUsage\n=====\n\n.. image:: https://travis-ci.org/rkhwaja/wccls.svg?branch=master\n   :target: https://travis-ci.org/rkhwaja/wccls\n\n.. code-block:: python\n\n  wccls = Wccls(login=cardNumber, password=password)\n  for item in wccls.items:\n      print(item)\n',
    'author': 'Rehan Khwaja',
    'author_email': 'rehan@khwaja.name',
    'url': 'https://github.com/rkhwaja/wccls',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.6',
}


setup(**setup_kwargs)
