# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['flake8_awesome']

package_data = \
{'': ['*']}

install_requires = \
['flake8-builtins>=1.4,<2.0',
 'flake8-comprehensions>=1.4,<2.0',
 'flake8-eradicate>=0.2.0,<0.3.0',
 'flake8-if-expr>=0.2.0,<0.3.0',
 'flake8-isort>=2.6,<3.0',
 'flake8-logging-format>=0.6.0,<0.7.0',
 'flake8-pie>=0.1.0,<0.2.0',
 'flake8-pytest>=1.3,<2.0',
 'flake8-quotes>=1.0,<2.0',
 'flake8>=3.7,<4.0',
 'pep8-naming>=0.8.0,<0.9.0']

setup_kwargs = {
    'name': 'flake8-awesome',
    'version': '0.1.0',
    'description': 'Flake8 awesome plugins pack',
    'long_description': '# flake8-awesome\n\n[![pypi](https://badge.fury.io/py/flake8-awesome.svg)](https://pypi.org/project/flake8-awesome)\n[![Python: 3.6+](https://img.shields.io/badge/Python-3.6+-blue.svg)](https://pypi.org/project/flake8-awesome)\n[![Downloads](https://img.shields.io/pypi/dm/flake8-awesome.svg)](https://pypistats.org/packages/flake8-awesome)\n[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](https://en.wikipedia.org/wiki/MIT_License)\n\nFlake8 awesome plugins pack.\n\n## Installation\n\n```bash\npip install flake8-awesome\n```\n\nand you have ONE dep in your requirements (pipfile, pyproject.toml)\n\nvs\n\n```bash\npip install flake8 flake8-builtins flake8-comprehensions flake8-eradicate # etc.\n```\n\n## Plugins\n\n* flake8-builtins\n* flake8-comprehensions\n* flake8-eradicate\n* flake8-if-expr\n* flake8-isort\n* flake8-logging-format\n* flake8-pie\n* flake8-pytest\n* flake8-quotes\n* pep8-naming\n\n## License\n\nMIT\n\n## Change Log\n\n### 0.1.0\n\n* initial\n',
    'author': 'Afonasev Evgeniy',
    'author_email': 'ea.afonasev@gmail.com',
    'url': 'https://pypi.org/project/flake8-awesome',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
