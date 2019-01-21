# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['blockbuster', 'blockbuster.core']

package_data = \
{'': ['*']}

install_requires = \
['marshmallow>=2.18,<3.0']

setup_kwargs = {
    'name': 'blockbuster-core',
    'version': '0.1.4',
    'description': '',
    'long_description': '.. image:: https://coveralls.io/repos/github/meatballs/blockbuster-core/badge.svg?branch=master\n  :target: https://coveralls.io/github/meatballs/blockbuster-core?branch=master\n\n.. image:: https://travis-ci.org/meatballs/blockbuster-core.svg?branch=master\n  :target: https://travis-ci.org/meatballs/blockbuster-core\n\n================\nBlockbuster Core\n================\nA Python interface (API) to `todo.txt <https://github.com/todotxt/todo.txt>`_\nfiles.\n\nIntroduction\n------------\nThis library will form the basis for several todo list management applications.\n\nIt will provide the interface to the underlying todo.txt files and functions to\nmanage the tasks stored within those files.\n\nInstallation\n------------\nSorry, there\'s nothing to install (yet)!\n\nUsage\n-----\nIt doesn\'t (yet) do anything at all!\n\nFAQ\n---\n\nWhy yet another todo manager?\n*****************************\nThe todo.txt format is simple, available to anyone free of charge, mature,\nstable, battle-tested and hardened.\n\nHowever, many of the alternative, propietary tools offer features which the\ntodo.txt based tools do not. e.g. the use of mulitiple lists rather than just\none.\n\nAlso, many people, myself included, use a range of different tools across\nmultiple devices and these do not always offer the same range of features.\n\nBy placing the management functions in a core library, this project aims to\nenable the creation of multiple client applications which have common features\nand behaviour.\n\nFor example, the author intends to create a command line interface (similar to\nthe `original shell program <https://github.com/todotxt/todo.txt-cli>`_), a\ntextual interface (similar to `todotxt-machine <https://github.com/AnthonyDiGirolamo/todotxt-machine>`_\nor `todd <https://github.com/laktak/todd>`_) and a mobile interface using `BeeWare <https://pybee.org/>`_.\n\nWhy call it Blockbuster?\n************************\nIt\'s a reference to the `1973 chart topping hit <https://www.youtube.com/watch?v=Y64211sjSko>`_\nby `The Sweet <https://en.wikipedia.org/wiki/The_Sweet>`_.\n\nThe song includes a line that was screamed incessantly by those of us on a UK\nschool playground that year to the constant irritation of our teachers:\n\n  "We just haven\'t got a clue what to do!"\n',
    'author': 'Owen Campbell',
    'author_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.6',
}


setup(**setup_kwargs)
