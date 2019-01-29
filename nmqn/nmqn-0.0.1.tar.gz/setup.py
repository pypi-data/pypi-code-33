# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['nmqn', 'nmqn._common', 'nmqn.compare', 'nmqn.crawl', 'nmqn.lib']

package_data = \
{'': ['*'], 'nmqn.compare': ['templetes/*']}

install_requires = \
['aiohttp>=3.5,<4.0',
 'click>=7.0,<8.0',
 'jinja2>=2.10,<3.0',
 'pweave>=0.30.3,<0.31.0',
 'pyppeteer>=0.0.25,<0.0.26',
 'pyyaml>=3.13,<4.0',
 'requests-html>=0.9.0,<0.10.0',
 'requests>=2.21,<3.0',
 'retry>=0.9.2,<0.10.0']

entry_points = \
{'console_scripts': ['nmqn = nmqn.main:main']}

setup_kwargs = {
    'name': 'nmqn',
    'version': '0.0.1',
    'description': '',
    'long_description': '# nmqn\n\nサイトの変更をCSSの差分でレポーティングするためのツールです。\n\n## Installation\n\npandocに依存しています。\n\n```bash\n# Macの場合\nbrew install pandoc\npip install nmqn\n```\n\n## Usage\n\n設定ファイルの仕様は、GitHubリポジトリの `sample.yaml` を確認してください。\n\n```bash\n# sample.yamlの設定を基にクロール\nnmqn crawl -c sample.yaml\n\n# 前日分と比較し、HTMLのレポートを生成\nnmqn compare -c sample.yaml\n```',
    'author': 'takeshi',
    'author_email': 'sci.and.eng@gmail.com',
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
