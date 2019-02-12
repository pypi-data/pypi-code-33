# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['django_admin_display']

package_data = \
{'': ['*']}

setup_kwargs = {
    'name': 'django-admin-display',
    'version': '1.0.0',
    'description': 'Simplifies the use of special attributes for the django admin.',
    'long_description': '# django-admin-display\n\n![Version](https://img.shields.io/pypi/v/django-admin-display.svg)\n![Build status](https://travis-ci.org/escaped/django-admin-display.png?branch=master)\n![Coverage](https://coveralls.io/repos/escaped/django-admin-display/badge.png?branch=master)\n![Python Versions](https://img.shields.io/pypi/pyversions/django-admin-display.svg)\n![License](https://img.shields.io/pypi/l/django-admin-display.svg)\n\nSimplifies the use of special attributes for the django admin and make mypy happy :)\n\n\n## Requirements\n\n- Python >= 3.6\n- Django >= 1.11\n\n\n## Why?\n\n\n\n\n## Development\n\nThis project is using [poetry](https://poetry.eustace.io/) to manage all\ndev dependencies.\nClone this repository and run\n\n      poetry develop\n\n\nto create a virtual enviroment with all dependencies.\nYou can now run the test suite using\n\n      poetry run pytest\n\n\nThis repository follows the [angular commit conventions](https://github.com/marionebl/commitlint/tree/master/@commitlint/config-angular).\n',
    'author': 'Alexander Frenzel',
    'author_email': 'alex@relatedworks.com',
    'url': 'https://github.com/escaped/django-admin-display',
    'packages': packages,
    'package_data': package_data,
    'python_requires': '>=3.6',
}


setup(**setup_kwargs)
