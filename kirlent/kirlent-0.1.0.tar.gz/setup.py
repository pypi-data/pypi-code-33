# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['kirlent']

package_data = \
{'': ['*']}

install_requires = \
['doit>=0.31,<0.32']

extras_require = \
{'kirlent_sphinx': ['kirlent_sphinx>=0.1,<0.2']}

entry_points = \
{'console_scripts': ['kirlent = kirlent.cli:main']}

setup_kwargs = {
    'name': 'kirlent',
    'version': '0.1.0',
    'description': 'Educational content management tools.',
    'long_description': 'Copyright (C) 2017-2019 H. Turgut Uyar <uyar@tekir.org>\n\nKırlent [#meaning]_ is a collection of utilities for managing educational\ncontent.\n\n:Repository: https://gitlab.com/tekir/kirlent\n:Documentation: https://kirlent.readthedocs.io/\n\nThe idea is to generate small units of content which can then be composed\ninto larger units. A unit can contain actual content, or it can also be\na collection that consists of other content units.\n\nKırlent uses `reStructuredText`_ as its markup language for source files.\nIt defines some extra syntax to simplify authoring.\n\nThe recommended structure all content units as folders under a main folder.\nEvery document should have the language code as a prefix to its\nfile extension::\n\n   content\n   |- expressions\n   |  |- slides.en.rst\n   |  `- slides.tr.rst\n   `- statements\n\nThe output folders for generated items will replicate this hierarchy, as in::\n\n   _build\n   |- expressions\n   |  |- slides.en.pdf\n   |  `- slides.tr.pdf\n   `- statement\n\nKırlent is built on the `doit`_ tool which makes it very easy to support\nincremental builds. That is, Kırlent will build an output again only if\nany of the relevant input files have changed.\n\n.. [#meaning]\n\n   "Kırlent" is a Turkish word which means a decorative pillow. It originates\n   from the Italian word "ghirlanda". It\'s also the name of `this beauty`_.\n\n.. _reStructuredText: http://docutils.sourceforge.net/rst.html\n.. _doit: http://pydoit.org/\n.. _this beauty: https://htuyar.tumblr.com/image/87196121163\n',
    'author': 'H. Turgut Uyar',
    'author_email': 'uyar@tekir.org',
    'url': 'https://gitlab.com/tekir/kirlent',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'entry_points': entry_points,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
