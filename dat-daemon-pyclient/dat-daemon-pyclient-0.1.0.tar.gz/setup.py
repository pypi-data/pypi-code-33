# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['dat_daemon_pyclient']

package_data = \
{'': ['*']}

install_requires = \
['asyncio>=3.4,<4.0',
 'grpcio-tools>=1.18,<2.0',
 'promise>=2.2,<3.0',
 'protobuf>=3.6,<4.0',
 'websockets>=7.0,<8.0']

setup_kwargs = {
    'name': 'dat-daemon-pyclient',
    'version': '0.1.0',
    'description': 'a client for the dat-daemon',
    'long_description': "# Dat daemon client\n\n## Installation\n\n```\npip install dat-daemon-pyclient\n```\n\n## Usage\n\n```python\nfrom dat_daemon_pyclient import DatDaemonClient\n\nclient = DatDaemonClient(url='ws://localhost:8447').run()\ndat = await client.add('/path/to/file_or_folder')\n```\n\n## API\n",
    'author': 'Rigel Kent',
    'author_email': 'sendmemail@rigelk.eu',
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
