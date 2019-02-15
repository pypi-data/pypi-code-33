# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['dotenver']

package_data = \
{'': ['*']}

install_requires = \
['colorama>=0.4.1,<0.5.0', 'faker>=1.0,<2.0', 'jinja2>=2.10,<3.0']

entry_points = \
{'console_scripts': ['dotenver = dotenver.cli:cli']}

setup_kwargs = {
    'name': 'dotenver',
    'version': '0.7.1',
    'description': 'Automatically generate .env files from .env.example template files',
    'long_description': '============================\nPython DotEnver\n============================\n\n.. image:: https://badge.fury.io/py/dotenver.svg\n    :target: https://badge.fury.io/py/dotenver\n\n.. image:: https://travis-ci.org/jmfederico/dotenver.svg?branch=master\n    :target: https://travis-ci.org/jmfederico/dotenver\n\n.. image:: https://img.shields.io/badge/code%20style-black-000000.svg\n    :target: https://github.com/ambv/black\n\nA Python app to generate dotenv (.env) files from templates.\n\n\nFeatures\n--------\n\n* Automatic .env file generation from .env.example files\n* Useful for CI or Docker deployments\n* Uses Jinja2_ as rendering engine\n* Uses Faker_ for value generation\n\n\nQuickstart\n----------\n\n1. Install **Python DotEnver**\n\n   .. code-block:: console\n\n    $ pip install dotenver\n\n2. Create a **.env.example** following this example\n\n   .. code-block:: ini\n\n    # Full line comments will be kept\n\n    # Simple usage\n    NAME= ## dotenver:first_name\n\n    # Pass parameters to fakers\n    ENABLED= ## dotenver:boolean(chance_of_getting_true=50)\n\n    # Name your values\n    MYSQL_PASSWORD= ## dotenver:password:my_password(length=20)\n    # And get the same value again, when the name is repeated.\n    DB_PASSWORD= ## dotenver:password:my_password()\n\n    # Output your values within double or single quotes\n    DOUBLE_QUOTED= ## dotenver:last_name(quotes=\'"\')\n    SINGLE_QUOTED= ## dotenver:last_name(quotes="\'")\n\n    # Literal values are possible\n    STATIC_VARIABLE=static value\n\n    # export syntax can be used\n    export EXPORTED_VARIABLE=exported\n\n3. Run python **DotEnver** form the CLI\n\n   .. code-block:: console\n\n    $ dotenver -r\n\n4. You now have a new **.env** file ready to use.\n\n5. For more usage options run\n\n   .. code-block:: console\n\n    $ dotenver -h\n\n\nDocker\n------\n\nA Docker image `is provided <Dotenver image_>`_. To use it, mount your source code to\n`/var/lib/dotenver/` and run the container.\n\n.. code-block:: console\n\n    $ docker run --rm -v `pwd`:/var/lib/dotenver/ jmfederico/dotenver\n\n.. _Faker: https://faker.readthedocs.io\n.. _Jinja2: http://jinja.pocoo.org\n.. _jmfederico: https://github.com/jmfederico\n.. _`Dotenver image`: https://hub.docker.com/r/jmfederico/dotenver\n',
    'author': 'Federico Jaramillo Martínez',
    'author_email': 'federicojaramillom@gmail.com',
    'url': 'https://github.com/jmfederico/dotenver',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
