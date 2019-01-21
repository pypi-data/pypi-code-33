# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['fastlane',
 'fastlane.api',
 'fastlane.cli',
 'fastlane.config',
 'fastlane.errors',
 'fastlane.models',
 'fastlane.worker']

package_data = \
{'': ['*'], 'fastlane': ['templates/*']}

install_requires = \
['Flask-Redis-Sentinel>=2.0,<3.0',
 'click>=6.7,<7.0',
 'derpconf>=0.8.2,<0.9.0',
 'docker>=3.4,<4.0',
 'flask-mongoengine>=0.9.5,<0.10.0',
 'flask-redis>=0.3.0,<0.4.0',
 'flask-sockets>=0.2.1,<0.3.0',
 'flask>=1.0,<2.0',
 'pybreaker>=0.4.5,<0.5.0',
 'python-dateutil>=2.7,<3.0',
 'pyyaml>=4.2b1,<5.0',
 'raven>=6.9,<7.0',
 'redis==2.10.6',
 'requests>=2.21,<3.0',
 'rq-dashboard>=0.3.12,<0.4.0',
 'rq-scheduler>=0.8.3,<0.9.0',
 'rq>=0.12.0,<0.13.0',
 'sentry-sdk==0.5.5',
 'structlog>=18.1,<19.0',
 'ujson>=1.35,<2.0',
 'wsaccel>=0.6.2,<0.7.0']

entry_points = \
{'console_scripts': ['fastlane = fastlane.cli:main', 'fl = fastlane.cli:main']}

setup_kwargs = {
    'name': 'fastlane',
    'version': '0.5.9',
    'description': 'fastlane is a redis and docker based queueing service.',
    'long_description': None,
    'author': 'Bernardo Heynemann',
    'author_email': 'heynemann@gmail.com',
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
