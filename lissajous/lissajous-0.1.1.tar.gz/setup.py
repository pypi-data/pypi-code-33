# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['lissajous']

package_data = \
{'': ['*']}

install_requires = \
['matplotlib>=3.0,<4.0', 'numpy>=1.16,<2.0']

entry_points = \
{'console_scripts': ['lissajous = lissajous.__main__:main']}

setup_kwargs = {
    'name': 'lissajous',
    'version': '0.1.1',
    'description': 'A Lissajous Curve Visualizer written in Python',
    'long_description': '<h1 align="center">lissajous</h1>\n<p align="center">\nA Lissajous Curve Visualizer written in Python<br><br>\n</p>\n\n\n<p align="center">\n<img src="https://github.com/kosayoda/lissajous/blob/master/docs/screens/intro.gif">\n</p>\n\n\n## Installation\n```\npip install lissajous\nlissajous\n```\n\n## Manual Installation\n### Requirements\n* Python 3.6+\n* numpy 1.16+\n* matplotlib 3.0+\n\n### Steps\n1. Click the **Clone or download** button in the top right corner then click **Download ZIP**\n2. Unpack the **zip file**\n3. Run the main script\n\n  ```\n  cd lissajous\n  python __main__.py\n\n  ```\n\n## Screenshots\n\n\n\n<p align="center">\n\n<img width="50%" src="docs/screens/img_1.png">\n\n<img width="50%" src="docs/screens/img_2.png">\n</p>\n\n## License\nThis project is licensed under MIT. For more information see the [LICENSE](https://github.com/kosayoda/lissajous/blob/master/LICENSE) file.\n\n',
    'author': 'kosayoda',
    'author_email': 'kieransiek@gmail.com',
    'url': 'https://github.com/kosayoda/lissajous',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
