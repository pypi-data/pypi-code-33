# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['copier']

package_data = \
{'': ['*']}

install_requires = \
['colorama>=0.4,<0.5', 'jinja2>=2.10,<3.0', 'ruamel.yaml>=0.15,<0.16']

entry_points = \
{'console_scripts': ['copier = copier.cli:run']}

setup_kwargs = {
    'name': 'copier',
    'version': '2.1.0',
    'description': 'A library for rendering projects templates',
    'long_description': '# Copier · [![](https://travis-ci.org/jpscaletti/copier.svg?branch=master)](https://travis-ci.org/jpscaletti/copier/) [![](https://img.shields.io/pypi/v/copier.svg)](https://pypi.python.org/pypi/copier) [![](https://img.shields.io/pypi/pyversions/copier.svg)](https://pypi.python.org/pypi/copier)\n\nA library for rendering projects templates.\n\n* Works with **local** paths and **git URLs**.\n* Your project can include any file and `Copier` can dynamically replace values in any kind of text files.\n* It generates a beautiful output and take care of not overwrite existing files, unless instructed to do so.\n\n![Sample output](https://github.com/jpscaletti/copier/raw/master/copier-output.png)\n\n\n## How to use\n\n- Use it in your Python code:\n\n```python\nfrom copier import copy\n\n# Create a project from a local path\ncopy(\'path/to/project/template\', \'path/to/destination\')\n\n# Or from a git URL.\ncopy(\'https://github.com/jpscaletti/copier.git\', \'path/to/destination\')\n\n# You can also use "gh:" as a shortcut of "https://github.com/"\ncopy(\'gh:jpscaletti/copier.git\', \'path/to/destination\')\n\n# Or "gl:"  as a shortcut of "https://gitlab.com/"\ncopy(\'gl:jpscaletti/copier.git\', \'path/to/destination\')\n```\n\n- Or as a command-line tool:\n\n```bash\ncopier path/to/project/template path/to/destination\n```\n\n\n## How it works\n\nThe content of the files inside the project template are copied to the destination\nwithout changes, **unless are suffixed with the extension \'.tmpl\'.**\nIn that case, the templating engine will be used to render them.\n\nA slightly customized Jinja2 templating is used. The main difference is\nthat variables are referenced with ``[[ name ]]`` instead of\n``{{ name }}`` and blocks are ``[% if name %]`` instead of\n``{% if name %}``. To read more about templating see the [Jinja2\ndocumentation](http://jinja.pocoo.org/docs>).\n\nIf a `copier.yml` is found in the root of the project, the user will be prompted to\nfill or confirm the values.\n\nUse the `data` argument to pass whatever extra context you want to be available\nin the templates. The arguments can be any valid Python value, even a\nfunction.\n\n\n## The copier.yml file\n\nIf a YAML file named `copier.yml` (alternatively, a `copier.json` ) is found in the root\nof the project, it will be read and used for two purposes:\n\n### Prompt the user for information\n\nFor each key found, Copier will prompt the user to fill or confirm the values before\nthey become avaliable to the project template. So a content like this:\n\n```yaml\nname_of_the_project: "My awesome project"\nyour_email: null\nnumber_of_eels: 1234\n```\n\nwill result in this series of questions:\n\n```shell\n\n   name_of_the_project? [My awesome project]\n   your_email? [None] myemail@gmail.com\n   number_of_eels? [1234] 42\n\n```\n\n### Arguments defaults\n\nThe keys `_exclude`, `_include` and `_tasks` in the `copier.yml` file, will be treated\nas the default values for the `exclude`, `include`, and `tasks` arguments to\n`copier.copy()`.\n\nNote that they become just *the default*, so any explicitely-passed argument will\noverwrite them.\n\n```yaml\n# Shell-style patterns files/folders that must not be copied.\n_exclude:\n    - *.bar\n\n# Shell-style patterns files/folders that *must be* copied, even if\n# they are in the exclude list\n-include:\n    - foo.bar\n\n# Commands to be executed after the copy\n_tasks:\n    - git init\n    - rm [[ name_of_the_project ]]/README.md\n\n```\n\n**Warning:** Use only trusted project templates as these tasks\nrun with the same level of access as your user.\n\n---\n\n## API\n\n#### copier.copy()\n\n`copier.copy(src_path, dst_path, data=None, *,\n    exclude=DEFAULT_FILTER, include=DEFAULT_INCLUDE, envops=None,\n    pretend=False, force=False, skip=False, quiet=False,\n)`\n\nUses the template in src_path to generate a new project at dst_path.\n\n**Arguments**:\n\n- **src_path** (str):\n    Absolute path to the project skeleton. May be a version control system URL\n\n- **dst_path** (str):\n    Absolute path to where to render the skeleton\n\n- **data** (dict):\n    Optional. Data to be passed to the templates in addtion to the user data from\n    a `copier.yml`.\n\n- **exclude** (list):\n    Optional. A list of names or shell-style patterns matching files or folders\n    that mus not be copied.\n\n- **include** (list):\n    Optional. A list of names or shell-style patterns matching files or folders that\n    must be included, even if its name are in the `exclude` list.\n    Eg: `[\'.gitignore\']`. The default is an empty list.\n\n- **tasks** (list):\n    Optional lists of commands to run in order after finishing the copy.\n    Like in the templates files, you can use variables on the commands that will\n    be replaced by the real values before running the command.\n    If one of the commands fail, the rest of them will not run.\n\n- **envops** (dict):\n    Optional. Extra options for the Jinja template environment.\n\n- **pretend** (bool):\n    Optional. Run but do not make any changes\n\n- **force** (bool):\n    Optional. Overwrite files that already exist, without asking\n\n- **skip** (bool):\n    Optional. Skip files that already exist, without asking\n\n- **quiet** (bool):\n    Optional. Suppress the status output\n',
    'author': 'Juan-Pablo Scaletti',
    'author_email': 'juanpablo@jpscaletti.com',
    'url': 'https://github.com/jpscaletti/copier',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.5,<4.0',
}


setup(**setup_kwargs)
