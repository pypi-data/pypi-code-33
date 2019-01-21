# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['project_manager', 'project_manager.commands', 'project_manager.tests']

package_data = \
{'': ['*'], 'project_manager.tests': ['dummy_project/*']}

install_requires = \
['PyYAML>=3.13,<4.0',
 'click>=7.0,<8.0',
 'pprint>=0.1.0,<0.2.0',
 'sh>=1.12,<2.0',
 'tqdm>=4.29,<5.0']

entry_points = \
{'console_scripts': ['project_manager = project_manager:main']}

setup_kwargs = {
    'name': 'project-manager',
    'version': '0.0.1',
    'description': 'Easily run a project with various configuration setups',
    'long_description': '# project_manager\n\nA utility which makes running the same projects with various configurations as easy as pie.\n\n\n## Installation\n\n```bash\n$ pip install project_manager\n```\n\n\n## Usage\n\nCheck out the [documentation](https://project-manager.readthedocs.io/).\n\n\n## Development notes\n\nRun tests:\n\n```bash\n$ pytest\n```\n',
    'author': 'kpj',
    'author_email': 'kpjkpjkpjkpjkpjkpj@gmail.com',
    'url': 'https://github.com/kpj/project_manager',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.6',
}


setup(**setup_kwargs)
