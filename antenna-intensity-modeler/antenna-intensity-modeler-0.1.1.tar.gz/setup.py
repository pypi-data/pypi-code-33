# -*- coding: utf-8 -*-
from distutils.core import setup

package_dir = \
{'': 'src'}

packages = \
['antenna_intensity_modeler']

package_data = \
{'': ['*']}

install_requires = \
['click>=7.0,<8.0',
 'matplotlib>=3.0,<4.0',
 'numpy>=1.15,<2.0',
 'pandas>=0.23,<0.24',
 'scipy>=1.1,<2.0']

setup_kwargs = {
    'name': 'antenna-intensity-modeler',
    'version': '0.1.1',
    'description': 'Create near-field plots of parabolic dish antennas.',
    'long_description': '=========================\nantenna-intensity-modeler\n=========================\n\n\n.. image:: https://img.shields.io/pypi/v/antenna_intensity_modeler.svg\n        :target: https://pypi.python.org/pypi/antenna_intensity_modeler\n\n.. image:: https://img.shields.io/travis/wboxx1/antenna-intensity-modeler.svg\n        :target: https://travis-ci.com/wboxx1/antenna-intensity-modeler.svg?branch=master\n        :alt: Build status on travis-ci\n\n.. image:: https://ci.appveyor.com/api/projects/status/wboxx1/branch/master?svg=true\n    :target: https://ci.appveyor.com/api/projects/status/a9phai3m3pxjwtt5?svg=true\n    :alt: Build status on Appveyor\n\n.. image:: https://pyup.io/repos/github/wboxx1/antenna-intensity-modeler/shield.svg\n     :target: https://pyup.io/repos/github/wboxx1/antenna-intensity-modeler/\n     :alt: Updates\n\n\n\nCreate near-field plots of parabolic dish antennas.\n\n\n* Free software: GNU General Public License v3\n\n* Documentation: https://wboxx1.github.io/antenna-intensity-modeler\n\n\n\nInstallation:\n-------------\n\n.. code-block:: console\n\n    $ pip install antenna-intensity-modeler\n\nFeatures\n--------\n\n* TODO\n\nCredits\n-------\n\nThis package was created with Cookiecutter_ and the `wboxx1/cookiecutter-pypackage`_ project template.\n\n.. _Cookiecutter: https://github.com/audreyr/cookiecutter\n.. _`wboxx1/cookiecutter-pypackage`: https://github.com/wboxx1/cookiecutter-pypackage-poetry\n',
    'author': 'Will Boxx',
    'author_email': 'wboxx1@gmail.com',
    'url': 'https://wboxx1.github.io/antenna-intensity-modeler',
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.5,<4.0',
}


setup(**setup_kwargs)
