# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['formation', 'formation.middleware']

package_data = \
{'': ['*']}

install_requires = \
['attrs>=18.2,<19.0',
 'cytoolz>=0.9.0,<0.10.0',
 'lxml>=4.2,<5.0',
 'pybreaker>=0.4.5,<0.5.0',
 'requests>=2.20,<3.0',
 'toolz>=0.9.0,<0.10.0',
 'xmltodict>=0.11.0,<0.12.0']

setup_kwargs = {
    'name': 'formation',
    'version': '0.1.30',
    'description': 'A generic functional middleware infrastructure for Python.',
    'long_description': '![](media/cover.png)\n\n# Formation\n\nA generic functional middleware infrastructure for Python.\n\nTake a look:\n\n```py\nfrom datetime.datetime import now\nfrom formation import wrap\nfrom requests import get\n\ndef log(ctx, call):\n    print("started")\n    ctx = call(ctx)\n    print("ended")\n    return ctx\n\ndef timeit(ctx, call):\n    started = now()\n    ctx = call(ctx)\n    ended = now() - started\n    ctx[\'duration\'] = ended\n    return ctx\n\ndef to_requests(ctx):\n    get(ctx[\'url\'])\n\nfancy_get = wrap(to_requests, middleware=[log, timeit])\nfancy_get({\'url\':\'https://google.com\'})\n```\n\n## Quick Start\n\nInstall using pip/pipenv/etc. (we recommend [poetry](https://github.com/sdispater/poetry) for sane dependency management):\n\n```\n$ poetry add formation\n```\n\n## Best Practices\n\nA `context` object is a loose bag of objects. With that freedom comes responsibility and opinion.\n\nFor example, this is how Formation models a `requests` integration, with data flowing inside `context`:\n\n\n* It models a `FormationHttpRequest` which abstracts the essentials of making an HTTP request (later shipped to `requests` itself in the way that it likes)\n* It tucks `FormationHttpRequest` under the `fmtn.req` key.\n* Additional information regarding such a request is kept _alongside_ `fmtn.req`. For example a request id is kept in the `req.id` key. This creates a flat (good thing) dict to probe. The reason additional data does not have the `fmtn` prefix is that you can always build your own that uses a different prefix (which you cant say about internal Formation inner workings).\n\n\n\n\n\n\n### Thanks:\n\nTo all [Contributors](https://github.com/jondot/formation/graphs/contributors) - you make this happen, thanks!\n\n# Copyright\n\nCopyright (c) 2018 [@jondot](http://twitter.com/jondot). See [LICENSE](LICENSE.txt) for further details.',
    'author': 'Dotan Nahum',
    'author_email': 'jondotan@gmail.com',
    'url': 'https://github.com/jondot/formation',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=2.7, !=3.0.*, !=3.1.*, !=3.2.*, !=3.3.*, !=3.4.*, !=3.5.*, !=3.6.*',
}


setup(**setup_kwargs)
