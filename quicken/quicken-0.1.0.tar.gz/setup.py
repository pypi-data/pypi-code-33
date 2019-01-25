# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['quicken']

package_data = \
{'': ['*']}

install_requires = \
['fasteners>=0.14.1,<0.15.0',
 'pid>=2.2,<3.0',
 'psutil>=5.4,<6.0',
 'python-daemon>=2.2,<3.0',
 'tblib>=1.3,<2.0']

setup_kwargs = {
    'name': 'quicken',
    'version': '0.1.0',
    'description': 'Make Python apps fast.',
    'long_description': "# quicken\n\nMake Python tools fast.\n\n```python\n# app/cli.py\nimport slow_module\nimport has_lots_of_dependencies\n\n\ndef cli():\n    print('hello world')\n    # Finally get to work after everything is loaded.\n    slow_module.do_work(has_lots_of_dependencies)\n    \n\n# app/main.py\nfrom quicken import cli_factory\n\n\n@cli_factory('app')\ndef main():\n    from .cli import cli\n    return cli\n```\n\nThat's it! The first time `main()` is invoked a server will be created and\nstay up even after the process finishes. When another process starts up it\nwill request the server to execute `cli` instead of reloading all modules\n(and dependencies) from disk. This relies on the speed of `fork` being lower\nthan the startup time of a typical cli application.\n\nIf `python -c ''` takes 10ms, this module takes around 40ms. That's how\nfast your command-line apps can start every time after the server is up.\n\n\n# Why\n\nPython command-line tools are slow. We can reduce dependencies, do lazy\nimporting, and do little/no work at the module level but these can only go\nso far.\n\nOur goal is to speed up the cli without giving up any dependencies. Every Python\nCLI tool should be able to get to work in less than 100ms.\n\n# Goals\n\n* Be as fast as possible when invoked as a client, be pretty fast when invoked\n  and we need to start a server.\n\n# Limitations\n\n* Unix only.\n* Debugging may be less obvious for end users or contributors.\n* Daemon will not automatically have updated gid list if user was modified.\n* Access to the socket file implies access to the daemon (and the associated command that it would run if asked).\n\n# Tips\n\n* Profile import time with -X importtime, see if your startup is actually the\n  problem. If it's not then this package will not help you.\n* Distribute your package as a wheel. When wheels are installed they create\n  scripts that do not import `pkg_resources`, which can save 60ms+ depending\n  on disk speed and caching.\n\n# Development\n\n```\nln -sf ../.githooks .git/hooks\n```\n",
    'author': 'Chris Hunt',
    'author_email': 'chrahunt@gmail.com',
    'url': 'https://github.com/chrahunt/quicken',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
