# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['susy_cross_section', 'susy_cross_section.tests']

package_data = \
{'': ['*'],
 'susy_cross_section': ['data/fastlim/8TeV/NLO+NLL/*',
                        'data/lhc_susy_xs_wg/*'],
 'susy_cross_section.tests': ['data/*']}

install_requires = \
['click>=7.0,<8.0', 'pandas>=0.24,<0.25', 'scipy>=1.2,<2.0']

extras_require = \
{':python_version >= "2.7.0" and python_version < "2.8.0"': ['pathlib>=1.0,<2.0',
                                                             'typing>=3.6,<4.0']}

entry_points = \
{'console_scripts': ['susy-xs-get = susy_cross_section.scripts:command_get',
                     'susy-xs-show = susy_cross_section.scripts:command_show']}

setup_kwargs = {
    'name': 'susy-cross-section',
    'version': '0.0.3',
    'description': 'A Python package for high-energy physics analysis to provide SUSY cross section data',
    'long_description': '[![Build Status](https://api.travis-ci.org/misho104/susy_cross_section.svg?branch=master)](https://travis-ci.org/misho104/susy_cross_section)\n[![Coverage Status](https://coveralls.io/repos/github/misho104/susy_cross_section/badge.svg?branch=master)](https://coveralls.io/github/misho104/susy_cross_section?branch=master)\n[![License: MIT](https://img.shields.io/badge/License-MIT-ff25d1.svg)](https://github.com/misho104/susy_cross_section/blob/master/LICENSE)\n\n[susy_cross_section](https://github.com/misho104/susy_cross_section): Table-format cross-section data handler\n=============================================================================================================\n\nA Python package for [cross section tables](https://twiki.cern.ch/twiki/bin/view/LHCPhysics/SUSYCrossSections) and interpolation.\n\nQuick Start\n-----------\n\nThis package supports Python 2.7 and 3.5+.\n\nInstall simply via PyPI and use a script as:\n\n```console\n$ pip install susy-cross-section\n$ susy-xs-get 13TeV.n2x1+.wino 500\n(32.9 +2.7 -2.7) fb\n$ susy-xs-get 13TeV.n2x1+.wino 513.3\n(29.4 +2.5 -2.5) fb\n```\n\nwhich gives the 13 TeV LHC cross section to wino-like neutralino-chargino pair-production (`p p > n2 x1+`), etc.\nThe values are taken from [LHC SUSY Cross Section Working Group](https://twiki.cern.ch/twiki/bin/view/LHCPhysics/SUSYCrossSections13TeVn2x1wino#Envelope_of_CTEQ6_6_and_MSTW_AN1) with interpolation if needed.\n\nYou can find a list of supported processes in [susy_cross_section/config.py](https://github.com/misho104/susy_cross_section/blob/master/susy_cross_section/config.py).\nIt is also straight forward to parse your own table files once you provide `.info` files as you find in [susy_cross_section/data/](https://github.com/misho104/susy_cross_section/tree/master/susy_cross_section/data/).\n\nYou can uninstall this package as simple as\n\n```console\n$ pip uninstall susy-cross-section\nUninstalling susy-cross-section-x.y.z:\n   ...\nProceed (y/n)?\n```\n\nIntroduction\n------------\n\nProduction cross sections are the most important values for high-energy physics collider experiments.\nThere are many sources for the values, evaluated in various tools or schemes.\nFor SUSY scenarios, the values provided by [LHC SUSY Cross Section Working Group](https://twiki.cern.ch/twiki/bin/view/LHCPhysics/SUSYCrossSections) are the most famous source of the "nominal" cross section expectation.\nHowever, their results as well as results provided in other references are not in machine-readable format and the data are provided in various format.\n\nThis package provides a module `susy_cross_section` to handle those data.\nAny table-like files can be interpreted and read as a [https://pandas.pydata.org/](pandas) DataFrame object, once an annotation file (`info` files in JSON format) is provided, so that one can easily interpolate the grid by, e.g., [scipy.interpolate](https://docs.scipy.org/doc/scipy/reference/interpolate.html).\n\nFor simpler use-case, a command-line script `susy-xs-get` is provided, with which one can get the cross section in several simple scenarios.\n\nSeveral data tables are included in this package, which is taken from, e.g., [LHC SUSY Cross Section Working Group](https://twiki.cern.ch/twiki/bin/view/LHCPhysics/SUSYCrossSections).\nIn addition, one can use their own files by writing annotations, so that they interpolate their data with pre-installed interpolator.\n\nMore information to use as a Python package will be given in API references (to be written), and to use as a script can be found in their help:\n\n```console\n$ susy-xs-get --help\nUsage: susy-xs-get [OPTIONS] TABLE ARGS...\n\n  Interpolate cross-section data using the standard scipy interpolator (with\n  log-log axes).\n\nOptions:\n  ...\n```\n\nLicense\n-------\n\nThe program codes included in this repository are licensed by [Sho Iwamoto / Misho](https://www.misho-web.com) under [MIT License](https://github.com/misho104/SUSY_cross_section/blob/master/LICENSE).\n\nOriginal cross-section data is distributed by other authors, including\n\n* [LHC SUSY Cross Section Working Group](https://twiki.cern.ch/twiki/bin/view/LHCPhysics/SUSYCrossSections).\n\nReferences (original data)\n--------------------------\n\n* https://twiki.cern.ch/twiki/bin/view/LHCPhysics/SUSYCrossSections\n\n* C. Borschensky, M. Kr\xc3\xa4mer, A. Kulesza, M. Mangano, S. Padhi, T. Plehn, X. Portell,\n  *Squark and gluino production cross sections in pp collisions at \\sqrt(s) = 13, 14, 33 and 100 TeV,*\n  [Eur. Phys. J. **C74** (2014) 12](https://doi.org/10.1140/epjc/s10052-014-3174-y)\n  [[arXiv:1407.5066](http://arxiv.org/abs/1407.5066)].\n\n* M. Kr\xc3\xa4mer, A. Kulesza, R. Leeuw, M. Mangano, S. Padhi, T. Plehn, X. Portell,\n  *Supersymmetry production cross sections in pp collisions at sqrt{s} = 7 TeV,*\n  [arXiv:1206.2892](https://arxiv.org/abs/1206.2892).\n\n* NNLL-fast: https://www.uni-muenster.de/Physik.TP/~akule_01/nnllfast/\n\n* W. Beenakker, C. Borschensky, M. Kr\xc3\xa4mer, A. Kulesza, E. Laenen,\n  *NNLL-fast: predictions for coloured supersymmetric particle production at the LHC with threshold and Coulomb resummation,*\n  [JHEP **1612** (2016) 133](https://doi.org/10.1007/JHEP12(2016)133)\n  [[arXiv:1607.07741](https://arxiv.org/abs/1607.07741)].\n',
    'author': 'Sho Iwamoto (Misho)',
    'author_email': 'webmaster@misho-web.com',
    'url': 'https://github.com/misho104/susy_cross_section',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'entry_points': entry_points,
    'python_requires': '>=2.7, !=3.0.*, !=3.1.*, !=3.2.*, !=3.3.*, !=3.4.*',
}


setup(**setup_kwargs)
