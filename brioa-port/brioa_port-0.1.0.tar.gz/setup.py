# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['brioa_port', 'brioa_port.scripts', 'brioa_port.util']

package_data = \
{'': ['*']}

install_requires = \
['Babel>=2.6,<3.0',
 'Pillow>=5.4,<6.0',
 'docopt>=0.6.2,<0.7.0',
 'numpy>=1.16,<2.0',
 'pandas>=0.23.4,<0.24.0',
 'python-dateutil>=2.7,<3.0',
 'schedule>=0.5.0,<0.6.0',
 'sqlalchemy>=1.2,<2.0',
 'tqdm>=4.30,<5.0',
 'xlrd_no_sector_corruption_check>=1.2,<2.0']

entry_points = \
{'console_scripts': ['brioa_schedule = brioa_port.scripts.brioa_schedule:main',
                     'brioa_timelapse_creator = '
                     'brioa_port.scripts.brioa_timelapse_creator:main',
                     'brioa_webcam_downloader = '
                     'brioa_port.scripts.brioa_webcam_downloader:main']}

setup_kwargs = {
    'name': 'brioa-port',
    'version': '0.1.0',
    'description': 'Tools for interpreting data relating to the seaport in Itapoá, Brazil.',
    'long_description': '# brioa_port\n\nTools for interpreting data relating to the seaport in [Itapoá, Brazil](http://www.portoitapoa.com.br/) (UN/LOCODE: BR IOA).\n\n![Timelapse example](https://raw.githubusercontent.com/yurihs/brioa_port/master/assets/timelapse_example.gif)\n\n\n## The tools\n\n**Webcam downloader:** The port administration provides a public [image feed](http://www.portoitapoa.com.br/camera/) from a webcam watching over the berthing areas. This tool makes it easy to download these pictures on a fixed interval, preserving the creation date in the filenames.\n\n**Schedule downloader:** A spreadsheet describing recent and scheduled ship arrivals, moorings, and sailings is made available in the [Programação de Navios](http://www.portoitapoa.com.br/servicos_programacao_navios/) page. This tool processes and inserts this information into a SQLite database, describing the changes in schedule over time for each ship.\n\n**Timelapse creator:** Using the aforementioned webcam and schedule data, this tool creates timelapse videos with augmented information, describing the ships that appear on screen.\n',
    'author': 'yurihs',
    'author_email': 'yurisalvador@hotmail.com',
    'url': 'https://github.com/yurihs/brioa_port',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
