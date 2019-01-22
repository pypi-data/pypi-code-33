# -*- coding: utf-8 -*-
from distutils.core import setup

package_dir = \
{'': 'src'}

modules = \
['nb_clean']
install_requires = \
['nbformat>=4.4,<5.0']

entry_points = \
{'console_scripts': ['nb-clean = nb_clean:main']}

setup_kwargs = {
    'name': 'nb-clean',
    'version': '1.3.0',
    'description': 'Clean Jupyter notebooks for versioning',
    'long_description': '# nb-clean\n\n`nb-clean` cleans Jupyter notebooks of cell execution counts, metadata, and\noutputs, preparing them for committing to version control. It provides a Git\nfilter to automatically clean notebooks before they are staged, and can also be\nused as a standalone tool outside Git or with other version control systems.\n\n## Installation\n\nTo install the latest release from [PyPI], use [pip]:\n\n```bash\npip install nb-clean\n```\n\nAlternately, in Python projects using [Poetry] or [Pipenv] for dependency\nmanagement, add `nb-clean` as a development dependency with\n`poetry add --dev nb-clean` or `pipenv install --dev nb-clean`. `nb-clean`\nrequires Python 3.6 or later.\n\n## Usage\n\nTo install a filter in an existing Git repository to automatically clean\nnotebooks before they are staged, run the following from the working tree:\n\n```bash\nnb-clean configure-git\n```\n\n`nb-clean` will configure a filter in the Git repository in which it is run, and\nwill not mutate your global or system Git configuration. To remove the filter,\nrun:\n\n```bash\nnb-clean unconfigure-git\n```\n\nAside from usage from a filter in a Git repository, you can also clean up a\nJupyter notebook manually with:\n\n```bash\nnb-clean clean -i original.ipynb -o cleaned.ipynb\n```\n\n## Copyright\n\nCopyright © 2017-2019 [Scott Stevenson].\n\n`nb-clean` is distributed under the terms of the [ISC licence].\n\n[isc licence]: https://opensource.org/licenses/ISC\n[pip]: https://pip.pypa.io/en/stable/\n[pipenv]: https://pipenv.readthedocs.io/en/latest/\n[poetry]: https://poetry.eustace.io/\n[pypi]: https://pypi.org/project/nb-clean/\n[scott stevenson]: https://scott.stevenson.io\n',
    'author': 'Scott Stevenson',
    'author_email': 'scott@stevenson.io',
    'url': 'https://github.com/srstevenson/nb-clean',
    'package_dir': package_dir,
    'py_modules': modules,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
