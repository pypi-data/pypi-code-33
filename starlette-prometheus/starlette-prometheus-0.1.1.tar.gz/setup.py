# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['starlette_prometheus']

package_data = \
{'': ['*']}

install_requires = \
['prometheus_client>=0.5.0,<0.6.0', 'starlette>=0.9.0']

setup_kwargs = {
    'name': 'starlette-prometheus',
    'version': '0.1.1',
    'description': 'Prometheus integration for Starlette',
    'long_description': '# Starlette Prometheus\n[![Build Status](https://travis-ci.org/PeRDy/starlette-prometheus.svg?branch=master)](https://travis-ci.org/PeRDy/starlette-prometheus)\n[![codecov](https://codecov.io/gh/PeRDy/starlette-prometheus/branch/master/graph/badge.svg)](https://codecov.io/gh/PeRDy/starlette-prometheus)\n[![PyPI version](https://badge.fury.io/py/starlette-prometheus.svg)](https://badge.fury.io/py/starlette-prometheus)\n\n* **Version:** 0.1.1\n* **Status:** Production/Stable\n* **Author:** José Antonio Perdiguero López\n\n## Introduction\n\nPrometheus integration for Starlette.\n\n## Requirements\n\n* Python 3.6+\n* Starlette 0.9+\n\n## Installation\n\n```console\n$ pip install starlette-prometheus\n```\n\n## Usage\n\nA complete example that exposes prometheus metrics endpoint under `/metrics/` path.\n\n```python\nfrom starlette.applications import Starlette\nfrom starlette_prometheus import metrics, PrometheusMiddleware\n\napp = Starlette()\n\napp.add_middleware(PrometheusMiddleware)\napp.add_route("/metrics/", metrics)\n```\n\n## Contributing\n\nThis project is absolutely open to contributions so if you have a nice idea, create an issue to let the community \ndiscuss it.',
    'author': 'José Antonio Perdiguero López',
    'author_email': 'perdy@perdy.io',
    'url': 'https://github.com/PeRDy/starlette-prometheus',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
