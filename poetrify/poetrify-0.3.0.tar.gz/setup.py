# -*- coding: utf-8 -*-
from distutils.core import setup

package_dir = \
{'': 'src'}

packages = \
['poetrify']

package_data = \
{'': ['*']}

install_requires = \
['cleo>=0.7.2,<0.8.0',
 'licensename>=0.4.2,<0.5.0',
 'requests>=2.21,<3.0',
 'tomlkit>=0.5.3,<0.6.0']

entry_points = \
{'console_scripts': ['poetrify = poetrify.cli:application.run']}

setup_kwargs = {
    'name': 'poetrify',
    'version': '0.3.0',
    'description': 'Pipfile to pyproject.toml for Poetry',
    'long_description': '# Poetrify\n\n[![Codacy Badge](https://api.codacy.com/project/badge/Grade/b6382d985bf745958b70832f6b356615)](https://app.codacy.com/app/hiro.ashiya/poetrify?utm_source=github.com&utm_medium=referral&utm_content=kk6/poetrify&utm_campaign=Badge_Grade_Settings)\n[![GitHub license](https://img.shields.io/badge/license-MIT-blue.svg?style=flat-square)](https://raw.githubusercontent.com/kk6/poetrify/master/LICENSE)\n[![PyPI](https://img.shields.io/pypi/v/poetrify.svg?style=flat-square)](https://pypi.python.org/pypi/poetrify)\n[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/ambv/black)\n\n## Installation\n\nPipfile or requirements.txt(this is trial) to pyproject.toml for Poetry.\n\n```bash\n$ pip install poetrify\n```\n\n### required\n\n- `poetry` command (See: https://poetry.eustace.io/docs/#installation )\n\n## Usage\n\n```bash\n$ poetrify\nPoetrify version 0.3.0\n\nUSAGE\n  poetrify [-h] [-q] [-v\xa0[<...>]] [-V] [--ansi] [--no-ansi] [-n] <command> [<arg1>] ... [<argN>]\n\nARGUMENTS\n  <command>              The command to execute\n  <arg>                  The arguments of the command\n\nGLOBAL OPTIONS\n  -h (--help)            Display this help message\n  -q (--quiet)           Do not output any message\n  -v (--verbose)         Increase the verbosity of messages: "-v" for normal output, "-vv" for more verbose output and\n                         "-vvv" for debug\n  -V (--version)         Display this application version\n  --ansi                 Force ANSI output\n  --no-ansi              Disable ANSI output\n  -n (--no-interaction)  Do not ask any interactive question\n\nAVAILABLE COMMANDS\n  completions            Generate completion scripts for your shell.\n  generate               Generate pyproject.toml from the source file\n  help                   Display the manual of a command\n```\n\nExample structure::\n```bash\n$ tree .\n.\n├── app.py\n├── LICENSE\n├── Pipfile\n└── Pipfile.lock\n```\n\nThe `generate` command sets the way for `poetry init`\n\n```bash\n$ poetrify generate\nGenerated init command:\n\npoetry init --dependency=rauth --dependency=requests --dependency=requests-cache --dependency=furl --dependency=arrow --dependency=pytest --dependency=responses --dev-dependency=pytest --dev-dependency=pytest-cov --dev-dependency=pytest-flake8 --dev-dependency=responses --dev-dependency=pytest-runner --license=MIT\n\nExecute the above command. Also, the following output is due to Poetry.\n\nThis command will guide you through creating your pyproject.toml config.\n\nPackage name [foo]:\n...\n```\n\n### Trial\n\nAlso supported to requirements.txt on a trial basis.\n\nPlease specify `requirements.txt` for` --src` option. The default value of this option is Pipfile.\n\n```bash\n$ poetry run pip freeze > requirements.txt\n\n$ cat requirements.txt\naspy.yaml==1.1.1\natomicwrites==1.2.1\nattrs==18.2.0\ncertifi==2018.11.29\ncfgv==1.4.0\nchardet==3.0.4\ncleo==0.7.2\nClick==7.0\nclikit==0.2.3\ncoverage==4.5.2\nidentify==1.1.8\nidna==2.8\nimportlib-metadata==0.8\nincremental==17.5.0\nJinja2==2.10\nlicensename==0.4.2\nMarkupSafe==1.1.0\nmore-itertools==5.0.0\nnodeenv==1.3.3\npastel==0.1.0\npluggy==0.8.1\n-e git+https://github.com/kk6/poetrify.git@63a861cba868298c896888f5104230c4a00896bb#egg=poetrify\npre-commit==1.14.2\npy==1.7.0\npylev==1.3.0\npytest==3.10.1\npytest-cov==2.6.1\nPyYAML==3.13\nrequests==2.21.0\nsix==1.12.0\ntoml==0.10.0\ntomlkit==0.5.3\ntowncrier==18.6.0\nUnidecode==1.0.23\nurllib3==1.24.1\nvirtualenv==16.2.0\nzipp==0.3.3\n\n$ poetry run poetrify generate -d -s requirements.txt\nGenerated init command:\n\npoetry init --dependency=cleo --dependency=licensename --dependency=pre-commit --dependency=pytest-cov --dependency=requests --dependency=tomlkit --dependency=towncrier --license=MIT\n```\n\nAs you can see, poetrify extract only descendants packages from all the packages listed in `requirements.txt` and pass only those to poetry. This is to prevent `pyproject.toml` from becoming full of package names.\n',
    'author': 'kk6',
    'author_email': 'hiro.ashiya@gmail.com',
    'url': 'https://github.com/kk6/poetrify',
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
