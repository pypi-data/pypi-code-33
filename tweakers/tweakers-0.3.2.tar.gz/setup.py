# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['tweakers']

package_data = \
{'': ['*']}

install_requires = \
['dateparser>=0.7.0,<0.8.0', 'requests-html>=0.9.0,<0.10.0']

setup_kwargs = {
    'name': 'tweakers',
    'version': '0.3.2',
    'description': 'A Python wrapper for tweakers.net',
    'long_description': '# Tweakers\n[![Build Status](https://travis-ci.org/timotk/tweakers.svg?branch=master)](https://travis-ci.org/timotk/tweakers)\n[![codecov](https://codecov.io/gh/timotk/tweakers/branch/master/graph/badge.svg)](https://codecov.io/gh/timotk/tweakers)\n[![PyPI](https://img.shields.io/pypi/v/tweakers.svg)](https://pypi.org/project/tweakers)\n![PyPI - Python Version](https://img.shields.io/pypi/pyversions/tweakers.svg)\n\nA Python wrapper for [tweakers.net](https://tweakers.net/)\n\n## Install\n```\npip install tweakers\n```\n\n## Usage\n```\nimport tweakers\n```\n\n### Gathering\nWith the `tweakers.gathering` module you can access the forum.\n#### Active topics\n```\nfor topic in tweakers.gathering.active_topics():\n    print(topic.title)\n```\n\n#### Search\n```\nfor topic in tweakers.gathering.search(\'tweakers.net\'):\n    print(topic.title)\n```\n\n### Topic\n#### Get comments for a specific topic\n```\ntopic = Topic("https://gathering.tweakers.net/forum/list_messages/1551828")\nfor comment in topic.comments(page=1):\n    print(comment.user.name, comment.text)\n```\n\n#### Generate new comments as they are added\n```\nfor comment in topic.comment_stream():\n    print(comment.user.name, comment.text)\n```\n\n### Login\n```\ntweakers.login("YOUR_USERNAME", "YOUR_PASSWORD")\n```\nNow you can access pages that are unavailable for logged out users:\n```\nfor topic in tweakers.gathering.bookmarks():\n    print(topic.name)\n```\n',
    'author': 'Timo',
    'author_email': None,
    'url': 'https://github.com/timotk/tweakers',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.6',
}


setup(**setup_kwargs)
