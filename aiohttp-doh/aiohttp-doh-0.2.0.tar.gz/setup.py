# -*- coding: utf-8 -*-
from distutils.core import setup

modules = \
['aiohttp_doh']
install_requires = \
['aiohttp>=3.5,<4.0']

setup_kwargs = {
    'name': 'aiohttp-doh',
    'version': '0.2.0',
    'description': 'DNS over HTTPS reslover for aiohttp',
    'long_description': "aiohttp-doh\n===========\n\nDNS over HTTPS reslover for aiohttp\n\n\nInstallation\n------------\n\n.. code-block:: bash\n\n   $ pip install aiohttp-doh\n\n\nManual Usage\n------------\n\nIf you want use manualy, you must import ``ClientSession`` in ``aiohttp.client``\nmodule and ``TCPConnector`` in ``aiohttp.connector`` module and ``DNSOverHTTPSResolver``\nin ``aiohttp_doh`` package.\n\n.. code-block:: python3\n\n   from aiohttp.client import ClientSession\n   from aiohttp.connector import TCPConnector\n\n   from aiohttp_doh import DNSOverHTTPSResolver\n\n   def my_client_session(*args, **kwargs):\n       resolver = DNSOverHTTPSResolver(endpoints=[\n           'https://cloudflare-dns.com/dns-query',\n       ])\n       connector = TCPConnector(resolver=resolver)\n       return ClientSession(*args, **kwargs, connector=connector)\n\n    async def main():\n       async with my_client_session() as session:\n           async with session.get('http://example.com') as resp:\n               data = await resp.text()\n\n       print(data)\n\n\nShortcut\n--------\n\nManual usage is too board. So I make shortcut to use easily.\nYou just replace ``aiohttp.ClientSession`` to ``aiohttp_doh.ClientSession``.\n\n.. code-block:: python3\n\n   from aiohttp_doh import ClientSession\n\n   async def main():\n       async with ClientSession() as session:\n           async with session.get('http://example.com') as resp:\n               data = await resp.text()\n\n       print(data)\n\n\nOptions\n-------\n\nYou can pass below parameter for configuration.\n\nendpoints\n  List of str. DNS over HTTPS endpoints.\n  Shortcut use `'https://dns.google.com/resolve'`\n  and `'https://cloudflare-dns.com/dns-query'` both in default.\n  You can also use others instead.\n\njson_loads\n  Function for loads json. default is Python builtin json module's one.\n  You can use third-party json library like simplejson or ujson.\n\nresolver_class\n  Internal DNS resolver class. Using for connect to endpoint.\n  default is aiohttp default.\n\n\nLicense\n-------\n\nMIT\n",
    'author': 'Kim Jin Su',
    'author_email': 'item4_hun@hotmail.com',
    'url': 'https://github.com/item4/aiohttp-doh/',
    'py_modules': modules,
    'install_requires': install_requires,
    'python_requires': '>=3.5.3',
}


setup(**setup_kwargs)
