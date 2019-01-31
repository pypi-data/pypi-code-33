# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['dat_daemon_pyclient']

package_data = \
{'': ['*']}

install_requires = \
['asyncio>=3.4,<4.0',
 'grpcio-tools>=1.18,<2.0',
 'protobuf-to-dict',
 'protobuf>=3.6,<4.0',
 'websockets>=7.0,<8.0']

setup_kwargs = {
    'name': 'dat-daemon-pyclient',
    'version': '0.2.0',
    'description': 'a client for the dat-daemon',
    'long_description': "# Dat daemon client\n\nThis is a Python client for the [dat-daemon](https://github.com/soyuka/dat-daemon). It doesn't run it, but\ncommunicates with it, letting it share data in the background.\n\nRFC for the dat daemon protocol is available [at dat-daemon](https://github.com/soyuka/dat-daemon/blob/73df8bf3c18342566ee79383da3df8e13d46b2f0/packages/protocol/README.md). It is not an official spec of the dat project (yet).\n\n## Installation\n\n```\npip install dat-daemon-pyclient\n```\n\n## Usage\n\n```python\nfrom dat_daemon_pyclient import DatDaemonClient\n\nclient = DatDaemonClient(url='ws://localhost:8447').run()\ndat = await client.add('/path/to/file_or_folder')\n```\n\n## API\n\nThe client supports the following methods:\n\n- **list**\n- **add**\n- **remove_list**\n- **start**\n- **remove**\n- **load**\n- **watch**\n- **mkdir**\n- **readdir**\n- **rmdir**\n- **unlink**\n- **info**\n- **create_read_stream**\n- **create_write_stream**\n",
    'author': 'Rigel Kent',
    'author_email': 'sendmemail@rigelk.eu',
    'url': 'https://framagit.org/synalp/olki/dat-daemon-pyclient',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
