# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['paypay']

package_data = \
{'': ['*']}

install_requires = \
['paypalrestsdk>=1.13,<2.0',
 'python-alipay-sdk>=1.9,<2.0',
 'wechatpy[cryptography]>=1.7,<2.0']

setup_kwargs = {
    'name': 'paypay',
    'version': '0.1.0',
    'description': '',
    'long_description': None,
    'author': 'Junyu Mu',
    'author_email': 'me@mujunyu.com',
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
