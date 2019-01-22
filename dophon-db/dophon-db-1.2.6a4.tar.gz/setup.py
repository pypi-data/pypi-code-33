# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['dophon_db',
 'dophon_db.const',
 'dophon_db.mysql',
 'dophon_db.mysql.binlog',
 'dophon_db.mysql.remote',
 'dophon_db.mysql.sql_util',
 'dophon_db.orm',
 'dophon_db.orm.db_obj',
 'dophon_db.orm.db_obj.function_class',
 'dophon_db.reader',
 'dophon_db.sqllite',
 'dophon_db.utils']

package_data = \
{'': ['*']}

install_requires = \
['PyMySQL', 'dophon-logger']

setup_kwargs = {
    'name': 'dophon-db',
    'version': '1.2.6a4',
    'description': 'dophon mysql module',
    'long_description': None,
    'author': 'CallMeE',
    'author_email': 'ealohu@163.com',
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
