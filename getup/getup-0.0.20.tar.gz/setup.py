# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['getup']

package_data = \
{'': ['*']}

install_requires = \
['dj_database_url>=0.5.0,<0.6.0',
 'django-cors-headers>=2.4,<3.0',
 'django-environ>=0.4.5,<0.5.0',
 'django>=2.1,<3.0',
 'dnspython>=1.16,<2.0',
 'email-validator>=1.0,<2.0',
 'pydantic>=0.19.0,<0.20.0']

entry_points = \
{'console_scripts': ['getup = getup.up:main']}

setup_kwargs = {
    'name': 'getup',
    'version': '0.0.20',
    'description': 'Projectless Django setup tool',
    'long_description': "\n# Getup\n\nProjectless Django setup tool\n\nSee Gitlab repository for small helper apps.\n\n## Getup config tool\n\nIncluded getup.py can function as projectless Django starter. Use provided sample conf file with it or substitute own with `GETUP_CONF_PATH` env variable.\n\nRun `python getup.py`, `./getup.py` or add the file into global $PATH to have it available everywhere there's Django app.\n\nFollowing settings can be set by env vars:\n\n  - GETUP_READ_ENV (set this to get others read)\n  - DATABASE_URL\n  - SECRET_KEY\n  - ALLOWED_HOSTS\n  - DATABASE_URL\n  - SENTRY_DSN\n",
    'author': 'Jussi Arpalahti',
    'author_email': 'jussi.arpalahti@gmail.com',
    'url': 'https://gitlab.com/jussiarpalahti/getup',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
