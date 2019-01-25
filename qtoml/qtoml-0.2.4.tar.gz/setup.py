# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['qtoml']

package_data = \
{'': ['*']}

entry_points = \
{'console_scripts': ['qtoml_testdecode = qtoml.__main__:decode',
                     'qtoml_testencode = qtoml.__main__:encode']}

setup_kwargs = {
    'name': 'qtoml',
    'version': '0.2.4',
    'description': 'New TOML encoder/decoder',
    'long_description': '*****\nqTOML\n*****\n\nqtoml is another Python TOML encoder/decoder. I wrote it because I found\nuiri/toml too unstable, and PyTOML too slow.\n\nFor information concerning the TOML language, see `toml-lang/toml <https://github.com/toml-lang/toml>`_.\n\nqtoml currently supports TOML v0.5.0.\n\nUsage\n=====\n\nqtoml supports the standard ``load``/``loads``/``dump``/``dumps`` API common to\nmost similar modules. Usage:\n\n.. code:: pycon\n\n  >>> import qtoml\n  >>> toml_string = """\n  ... test_value = 7\n  ... """\n  >>> qtoml.loads(toml_string)\n  {\'test_value\': 7}\n  >>> print(qtoml.dumps({\'a\': 4, \'b\': 5.0}))\n  a = 4\n  b = 5.0\n  \n  >>> infile = open(\'filename.toml\', \'r\')\n  >>> parsed_structure = qtoml.load(infile)\n  >>> outfile = open(\'new_filename.toml\', \'w\')\n  >>> qtoml.dump(parsed_structure, outfile)\n\nTesting\n=======\n\nqtoml is tested against the `alethiophile/toml-test <https://github.com/alethiophile/toml-test>`_ test suite, forked from\nuiri\'s fork of the original by BurntSushi. To run the tests, check out the code\nincluding submodules, install pytest, and run ``pytest`` under the ``tests``\nsubdirectory.\n\nLicense\n=======\n\nThis project is available under the terms of the MIT license.\n',
    'author': 'alethiophile',
    'author_email': 'tomdicksonhunt@gmail.com',
    'url': 'https://github.com/alethiophile/qtoml',
    'packages': packages,
    'package_data': package_data,
    'entry_points': entry_points,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
