# -*- coding: utf-8 -*-
from distutils.core import setup

package_dir = \
{'': 'src'}

packages = \
['xini']

package_data = \
{'': ['*']}

install_requires = \
['docopt>=0.6.2,<0.7.0', 'toml>=0.10.0,<0.11.0']

entry_points = \
{'console_scripts': ['xini = xini:main']}

setup_kwargs = {
    'name': 'xini',
    'version': '0.2.2',
    'description': '',
    'long_description': '### xini - eXtract pyproject.toml configs to INI\n\n`pyproject.toml` is a fantastic idea. I want all my tool configurations\nin my pyproject.toml file. Not all my tools support a `pyproject.toml`\nconfiguration option though, but why wait?\n\n`xini` pulls configurations from a `pyproject.toml` file for:\n\n   * pytest\n   * flake8\n   * coverage\n   * pylint\n\nAnd generates the appropriate ini-config files.\n\n\n### Install\n\n    ... pip install xini\n\n\n#### How Does It Work?\n\n1. Write tool configuration in the `pyproject.toml` under the appropriate "[tool.toolname]"\n   section. This becomes the standard location for your configurations.\n   Keep `pyproject.toml` in source control as normal.\n\n2. Run `xini` in the root project directory where the `pyproject.toml` file exits.\n   (`xini` does not search for `pyproject.toml` files anywhere but the current directory.)\n\n3. `xini` generates standard named ini-config files in the current directory\n   (e.g. .flake8, .coveragerc, etc.). Tools that use old-style ini file formats can then\n   run using the generated config file. **No need to maintain these ini-config files in source\n   control.**\n\n4. Make config changes in `pyproject.toml` and run `xini` to regnerate ini-config files.\n\n\n#### The Future\n\nIt is my sincere hope that there is no future for this project. I wish\nall tool developers to build support for `pyproject.toml` as a configuration\noption so a tool like `xini` is unnecessary.\n',
    'author': 'Mark Gemmill',
    'author_email': 'mark@markgemmill.com',
    'url': 'https://bitbucket.org/mgemmill/xini/src/master/',
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
