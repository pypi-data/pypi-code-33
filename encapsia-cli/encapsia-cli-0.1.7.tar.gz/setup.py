# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['encapsia_cli']

package_data = \
{'': ['*']}

install_requires = \
['awscli>=1.16,<2.0',
 'click>=7.0,<8.0',
 'encapsia-api>=0.1.7',
 'requests[security]>=2.20,<3.0',
 'toml>=0.10.0,<0.11.0']

entry_points = \
{'console_scripts': ['encapsia-add-superuser = encapsia_cli.add_superuser:main',
                     'encapsia-config = encapsia_cli.config:main',
                     'encapsia-dbctl = encapsia_cli.dbctl:main',
                     'encapsia-expire-token = encapsia_cli.expire_token:main',
                     'encapsia-plugins = encapsia_cli.plugins:main',
                     'encapsia-plugins-maker = encapsia_cli.plugins_maker:main',
                     'encapsia-schedule = encapsia_cli.schedule:main',
                     'encapsia-system-user = encapsia_cli.system_user:main',
                     'encapsia-task = encapsia_cli.task:main',
                     'encapsia-whoami = encapsia_cli.whoami:main']}

setup_kwargs = {
    'name': 'encapsia-cli',
    'version': '0.1.7',
    'description': 'Client CLI for talking to an Encapsia system.',
    'long_description': "# About\n\nThis package provides command line access to Encapsia over the REST API.\n\nAll of these are designed to work with server 1.5 and beyond.\n\n# TODO\n\n* Add some tests which exercise the command line, and illustrate it's use, with a real server.\n* Sync with https://bitbucket.org/cmedtechnology/icetools/src/6f7008db6133?at=refactor_tools\n* Check out https://bitbucket.org/cmedtechnology/iceapi/src/6a1093e0ae91/iceapi/?at=add_api\n* ice-copy-entities\n* ice-trialconfig",
    'author': 'Timothy Corbett-Clark',
    'author_email': 'timothy.corbettclark@gmail.com',
    'url': 'https://github.com/tcorbettclark/encapsia-cli',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
