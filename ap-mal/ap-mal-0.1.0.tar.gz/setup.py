# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['ap_mal']

package_data = \
{'': ['*']}

install_requires = \
['beautifulsoup4>=4.7,<5.0',
 'keyring>=17.1,<18.0',
 'lz4>=2.1,<3.0',
 'pycryptodome>=3.7,<4.0',
 'requests>=2.21,<3.0']

extras_require = \
{':sys_platform == "win32"': ['pywin32>=224.0,<225.0']}

entry_points = \
{'console_scripts': ['ap-mal = ap_mal.__main__:main']}

setup_kwargs = {
    'name': 'ap-mal',
    'version': '0.1.0',
    'description': 'Import and Export of lists between Anime-Planet and MyAnimeList',
    'long_description': '\nExport and import anime and manga lists on Anime-Planet and MyAnimeList.\n\n\nInstallation and usage\n======================\n\n.. code-block:: bash\n\n   pip install ap-mal\n   ap-mal --help\n\n\nExport from Anime-Planet\n========================\n\n.. code-block:: bash\n\n   ap-mal -e ap\n',
    'author': 'Christopher Goes',
    'author_email': 'ghostofgoes@gmail.com',
    'url': 'https://github.com/GhostofGoes/ap-mal',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'entry_points': entry_points,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
