# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['city_scrapers_core',
 'city_scrapers_core.commands',
 'city_scrapers_core.extensions',
 'city_scrapers_core.middlewares',
 'city_scrapers_core.pipelines',
 'city_scrapers_core.spiders']

package_data = \
{'': ['*'], 'city_scrapers_core': ['templates/*']}

install_requires = \
['jsonschema>=3.0.0a5',
 'legistar',
 'pytz>=2018.9,<2019.0',
 'requests>=2.21,<3.0',
 'scrapy>=1.5,<2.0']

extras_require = \
{'aws': ['boto3>=1.9'], 'azure': ['azure-storage-blob>=1.4']}

setup_kwargs = {
    'name': 'city-scrapers-core',
    'version': '0.1.0',
    'description': 'Core functionality for City Scrapers projects',
    'long_description': '# City Scrapers Core\n\nCore functionality for creating public meetings web scrapers for the [City Scrapers](https://cityscrapers.org/) project.\n\n## Installation\n\n`pip install city-scrapers-core`\n',
    'author': 'Pat Sier',
    'author_email': 'pat@citybureau.org',
    'url': 'https://cityscrapers.org/',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'python_requires': '>=3.5,<4.0',
}


setup(**setup_kwargs)
