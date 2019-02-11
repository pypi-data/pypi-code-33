# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['dophon',
 'dophon.annotation',
 'dophon.annotation.req',
 'dophon.annotation.res',
 'dophon.tools',
 'dophon.tools.framework_const',
 'dophon.tools.gc']

package_data = \
{'': ['*']}

install_requires = \
['dophon-logger',
 'dophon-manager',
 'dophon-properties',
 'flask',
 'gevent',
 'pyyaml>=3.13,<4.0',
 'schedule',
 'urllib3']

setup_kwargs = {
    'name': 'dophon',
    'version': '1.2.12.post7',
    'description': 'dophon web framework like springboot',
    'long_description': None,
    'author': 'CallMeE',
    'author_email': 'ealohu@163.com',
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
