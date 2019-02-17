# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['cimpyorm',
 'cimpyorm.Model',
 'cimpyorm.Test',
 'cimpyorm.Test.Deployment',
 'cimpyorm.Test.Integration',
 'cimpyorm.Test.Integration.MariaDB',
 'cimpyorm.Test.Integration.MySQL',
 'cimpyorm.Test.Integration.SQLite']

package_data = \
{'': ['*'],
 'cimpyorm': ['res/*',
              'res/datasets/FullGrid/*',
              'res/datasets/MiniGrid_BusBranch/*',
              'res/datasets/MiniGrid_NodeBreaker/*',
              'res/schemata/CIM16/*']}

install_requires = \
['lxml>=4.2,<5.0',
 'networkx>=2.2,<3.0',
 'numpy>=1.15,<2.0',
 'pandas>=0.24.1,<0.25.0',
 'pytest>=4.0,<5.0',
 'sphinx-autodoc-typehints>=1.6,<2.0',
 'sqlalchemy>=1.2,<2.0',
 'tabulate>=0.8.3,<0.9.0']

setup_kwargs = {
    'name': 'cimpyorm',
    'version': '0.4.0',
    'description': 'A database-backed ORM for CIM datasets.',
    'long_description': '## Installation\n\n###### PyPI:\n\n```pip install cimpyorm```\n\n---\n## Usage\n```python\nimport cimpyorm\n```\n\n---\n##### Loading datasets from cimpyorm-.db file\n```python\nsession, m = cimpyorm.load(r"Path/To/DatabaseFile") # Load an existing .db file\n```\n\n---\n##### Parsing datasets\n```python\nsession, m = cimpyorm.parse(r"Path/To/Folder/Containing/Export") # Parse a .xml export (also creates a cimpyorm-.db file of the export)\n```\nTo configure additional schemata (currently only the schema for the CGMES profiles are distributed\nwith the application), create additional subfolders in the ```/res/schemata/``` directory \ncontaing the schema RDFS.\n\n---\n##### Running the tests\nYou can run the included test-suite by running ```cimpyorm.test_all()```.\n\n---\n##### Querying datasets\n```python\nall_terminals = session.query(m.Terminal).all()\nnames_of_ConductingEquipment = [t.ConductingEquipment.name for t in all_terminals]\n```\n\n---\n## Bug reports/feature requests\nPlease use the Issue Tracker.',
    'author': 'Thomas Offergeld',
    'author_email': 'offergeld@ifht.rwth-aachen.de',
    'url': 'http://www.ifht.rwth-aachen.de',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
