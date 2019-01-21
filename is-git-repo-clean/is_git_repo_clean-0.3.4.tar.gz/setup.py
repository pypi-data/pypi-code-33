# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['is_git_repo_clean']

package_data = \
{'': ['*']}

entry_points = \
{'console_scripts': ['is-git-repo-clean = is_git_repo_clean.script:main']}

setup_kwargs = {
    'name': 'is-git-repo-clean',
    'version': '0.3.4',
    'description': 'A simple function to test whether your git repo is clean',
    'long_description': "## Is Git Repo Clean\n\n<!-- START doctoc generated TOC please keep comment here to allow auto update -->\n<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->\n**Table of Contents**\n\n- [Intro](#intro)\n    - [What is it?](#what-is-it)\n    - [Why create it?](#why-create-it)\n- [Install](#install)\n- [Usage](#usage)\n    - [programmatic](#programmatic)\n    - [cli](#cli)\n- [Api](#api)\n    - [`check` async (dir=os.getcwd()) => bool](#check-async-dirosgetcwd--bool)\n    - [`checkSync` (dir=os.getcwd()) => bool](#checksync-dirosgetcwd--bool)\n    - [`version`](#version)\n- [Test](#test)\n\n<!-- END doctoc generated TOC please keep comment here to allow auto update -->\n\n<br>\n\n### Intro\n\n#### What is it?\n\nA simple function that tests whether your git repo is clean.\n\nby *clean* I mean it has:\n- no untracked files\n- no staged changes\n- no unstaged changes\n\nInstalling this also exposes a cli command `is-git-repo-clean`\n\n\n#### Why create it?\n\nI wanted to write a build script that would exit early if the git repo\nwasn't clean\n\n<br>\n\n### Install\n\n```sh\n$ pip install is_git_repo_clean\n```\n\n<br>\n\n### Usage\n\n#### programmatic\n\n```python\nimport is_git_repo_clean\n\n\nasync def isCleanAsync(pathToGitRepo = None):\n  # async by default\n   return await is_git_repo_clean.check(pathToGitRepo)\n\n\ndef isCleanSync(pathToGitRepo = None):\n  # sync available\n  return is_git_repo_clean.checkSync(pathToGitRepo)\n```\n\n#### cli\n\n```sh\n$ is-git-repo-clean --help\n\nUsage\n  is-git-repo-clean [--dir <path>] [--silent]\n  is-git-repo-clean --help\n  is-git-repo-clean --version\n\nOptions\n  dir:      path to the git repo to test.  Defaults to `os.getcwd()`\n  silent:   disables output\n  help:     print this\n  version:  prints the version of this tool\n\nReturns\n  <exit code>: <output>\n\n  0: yes\n  1: no\n  2: <invalid arg message>\n  3: dir is not a git repository\n  4: unexpected error occurred <error>\n```\n\n<br>\n\n### Api\n\n`is_git_repo_clean` exports the following\n\n\n#### `check` async (dir=os.getcwd()) => bool\n - an asynchronous function that returns whether the git repo is clean\n\n\n#### `checkSync` (dir=os.getcwd()) => bool\n - a synchronous function that returns whether the git repo is clean\n\n\n#### `version`\n\n<br>\n\n### Test\n\n```sh\nhub clone olsonpm/py_is-git-repo-clean\ncd py_is-git-repo-clean\npython runTests.py\n```\n",
    'author': 'Philip Olson',
    'author_email': 'philip.olson@pm.me',
    'url': 'https://github.com/olsonpm/py_is-git-repo-clean',
    'packages': packages,
    'package_data': package_data,
    'entry_points': entry_points,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
