# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['proper']

package_data = \
{'': ['*']}

setup_kwargs = {
    'name': 'proper',
    'version': '0.1.0',
    'description': 'Conventions over configuration web framework',
    'long_description': '\n# Proper Web Framework\n\n*Conventions over configuration*\n\n\n### Requirements\n\n- Python 3.6+\n\n\n## Design principles\n\n- "Conventions over configuration".\n\n- No globals.\n\tWhen you need a shared object, pass it arround.\n\n- Optimize for the 95%.\n\tDon\'t compromise the usability of the common cases to keep consistency\n\twith the edge cases.\n\n- Code redability is very important.\n\n- App-code over framework-code\n\tBecause app code is infintely configurable without dirty hacks.\n\n- "Everyone is an adult here".\n\tRun with scissors if you must.\n\n- Greenthtreads over async\n',
    'author': 'Juan-Pablo Scaletti',
    'author_email': 'juanpablo@jpscaletti.com',
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
