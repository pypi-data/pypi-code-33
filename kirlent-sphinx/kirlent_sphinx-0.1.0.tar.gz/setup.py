# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['kirlent_sphinx']

package_data = \
{'': ['*'],
 'kirlent_sphinx': ['templates/kirlent/*',
                    'templates/kirlent/static/*',
                    'templates/kirlent/static/css/*',
                    'templates/kirlent/static/css/print/*',
                    'templates/kirlent/static/css/theme/*',
                    'templates/kirlent/static/css/theme/source/*',
                    'templates/kirlent/static/css/theme/template/*',
                    'templates/kirlent/static/js/*',
                    'templates/kirlent/static/lib/css/*',
                    'templates/kirlent/static/lib/font/league-gothic/*',
                    'templates/kirlent/static/lib/font/source-sans-pro/*',
                    'templates/kirlent/static/lib/js/*',
                    'templates/kirlent/static/plugin/highlight/*',
                    'templates/kirlent/static/plugin/leap/*',
                    'templates/kirlent/static/plugin/markdown/*',
                    'templates/kirlent/static/plugin/math/*',
                    'templates/kirlent/static/plugin/multiplex/*',
                    'templates/kirlent/static/plugin/notes-server/*',
                    'templates/kirlent/static/plugin/notes/*',
                    'templates/kirlent/static/plugin/postmessage/*',
                    'templates/kirlent/static/plugin/print-pdf/*',
                    'templates/kirlent/static/plugin/remotes/*',
                    'templates/kirlent/static/plugin/search/*',
                    'templates/kirlent/static/plugin/zoom-js/*']}

install_requires = \
['sphinx>=1.8,<2.0']

setup_kwargs = {
    'name': 'kirlent-sphinx',
    'version': '0.1.0',
    'description': 'Sphinx extension for slides and extended tables.',
    'long_description': 'Copyright (C) 2019 H. Turgut Uyar <uyar@tekir.org>\n\nkirlent_sphinx is a Sphinx extension that is primarily meant to be used with\nthe Kirlent educational content management system, although it can be used\nas a regular Sphinx extension. It consists of the following components:\n\n- An extended ``table`` directive derived from the `cloud_sptheme`_ package.\n\n- A ``slide`` directive and a corresponding, RevealJS-based HTML theme derived\n  from the `sphinxjp.themes.revealjs`_ package.\n\nThe changes to cloud_sptheme are very small at the moment and the documentation\nfor the original package should apply. There are some changes to note with\nrespect to the sphinxjp.themes.revealjs package:\n\n- The ``revealjs`` directive has been renamed to ``slide``.\n\n- The ``rv_note`` directive has been renamed to ``speaker-notes``.\n\n- The ``rv_small`` and ``rv_code`` directives have been removed.\n\n- The HTML theme uses pygments instead of highlight.js.\n\n- The HTML theme uses `bulma`_ for styling. So, for example, you can write\n  something like::\n\n    .. slide:: Slide Title\n\n       .. container:: columns\n\n          .. container:: column is-one-third\n\n             - item 1\n             - item 2\n\n          .. container:: column is-two-thirds\n\n             - item 3\n\n.. _cloud_sptheme: https://cloud-sptheme.readthedocs.io/en/latest/lib/cloud_sptheme.ext.table_styling.html\n.. _sphinxjp.themes.revealjs: https://github.com/tell-k/sphinxjp.themes.revealjs\n.. _bulma: https://bulma.io/\n',
    'author': 'H. Turgut Uyar',
    'author_email': 'uyar@tekir.org',
    'url': 'https://gitlab.com/tekir/kirlent_sphinx',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
