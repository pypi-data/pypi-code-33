# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['cognitivecluster']

package_data = \
{'': ['*']}

install_requires = \
['numpy>=1.16,<2.0',
 'scikit-learn>=0.20.2,<0.21.0',
 'tensorflow-hub>=0.2.0,<0.3.0',
 'tensorflow>=1.12,<2.0']

setup_kwargs = {
    'name': 'cognitivecluster',
    'version': '0.1.2',
    'description': 'A library to cluster partners based on metacognitive diversity',
    'long_description': '# Cognitive Cluster\n[![Build Status](https://travis-ci.org/mjs2600/cognitivecluster.svg?branch=master)](https://travis-ci.org/mjs2600/cognitivecluster)\n\nCognitive Cluster is a library for clustering written metacognitive exercises based on document embeddings.\nThis is useful for creating cross-cluster partnerships to increase the diversity of problem solving techniques in teams.',
    'author': 'Michael Simpson',
    'author_email': 'michael@snthesis.com',
    'url': 'https://github.com/mjs2600/cognitivecluster',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.6,<3.7',
}


setup(**setup_kwargs)
