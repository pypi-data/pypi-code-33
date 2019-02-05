# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['red_connector_http']

package_data = \
{'': ['*']}

install_requires = \
['cc-connector-cli>=0.3.0,<0.4.0',
 'jsonschema>=2.6,<3.0',
 'requests>=2.18,<3.0']

entry_points = \
{'console_scripts': ['red-connector-http = red_connector_http.main:main',
                     'red-connector-http-json = '
                     'red_connector_http.main_json:main',
                     'red-connector-http-mock-send = '
                     'red_connector_http.main_mock_send:main']}

setup_kwargs = {
    'name': 'red-connector-http',
    'version': '0.3',
    'description': 'RED Connector HTTP is part of the Curious Containers project.',
    'long_description': '# RED Connector HTTP\n\nRED Connector HTTP is part of the Curious Containers project.\n\nFor more information please refer to the Curious Containers [documentation](https://www.curious-containers.cc/).\n\n## Acknowledgements\n\nThe Curious Containers software is developed at [CBMI](https://cbmi.htw-berlin.de/) (HTW Berlin - University of Applied Sciences). The work is supported by the German Federal Ministry of Economic Affairs and Energy (ZIM project BeCRF, grant number KF3470401BZ4), the German Federal Ministry of Education and Research (project deep.TEACHING, grant number 01IS17056 and project deep.HEALTH, grant number 13FH770IX6) and HTW Berlin Booster.\n',
    'author': 'Christoph Jansen',
    'author_email': 'Christoph.Jansen@htw-berlin.de',
    'url': 'https://curious-containers.github.io/',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.4,<4.0',
}


setup(**setup_kwargs)
