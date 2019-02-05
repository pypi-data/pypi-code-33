# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['cc_connector_cli']

package_data = \
{'': ['*']}

setup_kwargs = {
    'name': 'cc-connector-cli',
    'version': '0.3',
    'description': 'CC Connector CLI is part of the Curious Containers project.',
    'long_description': '# CC Connector CLI\n\nCC Connector CLI is part of the Curious Containers project.\n\nFor more information please refer to the Curious Containers [documentation](https://www.curious-containers.cc/).\n\n## Acknowledgements\n\nThe Curious Containers software is developed at [CBMI](https://cbmi.htw-berlin.de/) (HTW Berlin - University of Applied Sciences). The work is supported by the German Federal Ministry of Economic Affairs and Energy (ZIM project BeCRF, grant number KF3470401BZ4), the German Federal Ministry of Education and Research (project deep.TEACHING, grant number 01IS17056 and project deep.HEALTH, grant number 13FH770IX6) and HTW Berlin Booster.\n',
    'author': 'Bruno Schilling',
    'author_email': 's0555131@htw-berlin.de',
    'url': 'https://curious-containers.github.io/',
    'packages': packages,
    'package_data': package_data,
    'python_requires': '>=3.4,<4.0',
}


setup(**setup_kwargs)
