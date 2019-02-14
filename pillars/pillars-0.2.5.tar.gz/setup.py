# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['pillars',
 'pillars.engines',
 'pillars.middlewares',
 'pillars.sites',
 'pillars.transports']

package_data = \
{'': ['*']}

install_requires = \
['aiodns>=1.1,<2.0',
 'aiohttp>=3.3,<4.0',
 'aioredis>=1.1,<2.0',
 'aiosip',
 'async-timeout>=3.0,<4.0',
 'asyncpg>=0.17.0,<0.18.0',
 'attrs>=18.1,<19.0',
 'cchardet>=2.1,<3.0',
 'cerberus>=1.2,<2.0',
 'cython>=0.28.5,<0.29.0',
 'panoramisk',
 'pyyaml>=3.13,<4.0',
 'setproctitle>=1.1,<2.0',
 'ujson>=1.35,<2.0',
 'uvloop>=0.11.2,<0.12.0']

setup_kwargs = {
    'name': 'pillars',
    'version': '0.2.5',
    'description': 'Collection of helpers for building asyncio daemons.',
    'long_description': '`Pillars <http://pypillars.readthedocs.io>`_\n============================================\n\nCollection of helpers for building asyncio daemons.\n\n.. image:: https://readthedocs.org/projects/pypillars/badge/?version=latest\n    :target: http://pypillars.readthedocs.io/en/latest/\n    :alt: Documentation Status\n.. image:: https://travis-ci.org/Eyepea/pillars.svg?branch=master\n    :target: https://travis-ci.org/Eyepea/pillars\n    :alt: Travis-ci status\n.. image:: https://badge.fury.io/py/pillars.svg\n    :target: https://pypi.org/project/pillars/\n    :alt: PyPI status\n\nInstallation\n------------\n\nPillars is `available on PyPI <https://pypi.org/project/pillars/>`_.\n\n.. code::\n\n    $ pip3 install pillars\n\nQuickstart\n----------\n\n.. code-block:: python\n\n    import pillars\n    import aiohttp\n\n    app = pillars.Application(name="example")\n    http = pillars.transports.http.Application()\n\n    app.listen(\n        app=http,\n        name="http",\n        runner=aiohttp.web.AppRunner(http),\n        sites=(functools.partial(aiohttp.web.TCPSite, host="127.0.01", port=8080),),\n    )\n\n    http.router.add_route("GET", "/", hello_world)\n\n    async def hello_world(request):\n        return pillars.Response(status=200, data={"data": "Hello world"})\n\nFor more examples see the `examples folder <https://github.com/eyepea/pillars/tree/master/examples>`_.\n\nChangelog\n---------\n\n0.2.4\n`````\n\n* Bugfix for `json_encoder` argument\n\n0.2.3\n`````\n\n* Add custom json encoder for UUID\n* Add `json_encoder` argument to `pillars.Response`\n\n0.2.2\n`````\n\n* Fix ARI engine shutdown\n\n0.2.1\n`````\n\n* Properly close websocket connection\n* Remove pg uuid encoder\n* Log when pg jsonb encode fails\n* Use aiohttp exception for ARI transports\n\n0.1.1\n`````\n\n* Initial release\n',
    'author': 'Allocloud',
    'author_email': 'allocloud@ovv.wtf',
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
