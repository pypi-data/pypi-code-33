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
    'version': '0.0.21',
    'description': 'Projectless Django setup tool',
    'long_description': "\n# Getup\n\nProjectless Django setup tool. Getup combines functionality of manage.py and wsgi module. It allows one Django app to be used as a service.\n\nSee Gitlab repository for app examples.\n\n## Getup config command\n\nRun `getup/up.py` or add as package to virtual env. It will work everywhere there's a Django app with configuration instantiation.\n\nAll settings can be set by configuration object or using environment variables or both. Configuration object is a Pydantic schema along with extension schemas. See `getup/conf.py` for complete set or accompanying example apps. This schema corresponds to usual Django settings.\n",
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
