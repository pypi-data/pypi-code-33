# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['results']

package_data = \
{'': ['*']}

install_requires = \
['chardet',
 'csvx',
 'furl',
 'logx',
 'markdown',
 'migra',
 'pendulum',
 'psycopg2-binary',
 'sqlalchemy',
 'sqlbag>=0.1.1548994599',
 'tabulate']

extras_require = \
{'excel': ['xlrd', 'openpyxl<2.5.10']}

setup_kwargs = {
    'name': 'results',
    'version': '0.1.1549324146',
    'description': "Don't get mad, get results",
    'long_description': '# Don\'t get mad, get `results`\n\nTabular data and SQL for people who don\'t have time to faff about.\n\nMove between xlsx, xls, csv, python, postgres and back with ease.\n\nFeatures:\n\n- Zero-boilerplate database creating, connecting and querying.\n- Loading/tidying/transforming csv and excel data.\n- Autodetect column types, load your data with little or no manual specification.\n- Powerful multi-column, multi-order keyset paging of database results.\n- Schema syncing.\n\nLimitations\n\n- Python 3.6+, PostgreSQL 10+ only. Many features will work with other databases, but many won\'t. Just use Postgres!\n\n# Installation\n\n[`results` is on PyPI](https://pypi.org/project/results). Install it with `pip` or any of the (many) Python package managers.\n\n## Scenario\n\nSomebody gives you a messy csv or excel file. You need to load it, clean it up, put it into a database, query it, make a pivot table from it, then send the pivot table to somebody as a csv.\n\n`results` is here to get this sort of thing done quickly and with minimum possible fuss.\n\nLet\'s see.\n\nFirst, load and clean:\n\n```python\nimport results\n\n# load a csv (in this example, some airport data)\nsheet = results.from_file("airports.csv")\n\n# do general cleanup\nsheet.standardize_spaces()\nsheet.set_blanks_to_none()\n\n# give the keys lowercase-with-underscore names to keep the database happy\ncleaned = sheet.with_standardized_keys()\n```\n\nThen, create a database:\n\n```python\n# create a database\nDB = "postgresql:///example"\n\ndb = results.db(DB)\n\n# create it if it doesn\'t exist\ndb.create_database()\n```\n\nThen create a table for the data, automatically guessing the columns and creating a table to match.\n\n```python\n# guess the column types\nguessed = cleaned.guessed_sql_column_types()\n\n# create a table for the data\ncreate_table_statement = results.create_table_statement("data", guessed)\n\n# create or auto-update the table structure in the database\n# syncing requires a copy of postgres running locally with your current user set up as superuser\ndb.sync_db_structure_to_definition(create_table_statement, confirm=False)\n```\n\nThen insert the data and freely query it.\n\n```python\n# insert the data. you can also do upserts with upsert_on!\ndb.insert("data", cleaned)\n\n# show recent airfreight numbers from the top 5 airports\n# ss means "single statement"\nquery_result = db.ss(\n    """\nwith top5 as (\n    select\n        foreignport, sum(freight_in_tonnes)\n    from\n        data\n    where year >= 2010\n    group by\n        foreignport\n    order by 2 desc\n    limit 5\n)\n\nselect\n    year, foreignport, sum(freight_in_tonnes)\nfrom\n    data\nwhere\n    year >= 2010\n    and foreignport in (select foreignport from top5)\ngroup by 1, 2\norder by 1, 2\n\n"""\n)\n```\n\nCreate a pivot table, then print it as markdown or save it as csv.\n\n```python\n# create a pivot table\npivot = query_result.pivoted()\n\n# print the pivot table in markdown format\nprint(pivot.md)\n```\n\nOutput:\n\n```\n|   year |   Auckland |    Dubai |   Hong Kong |   Kuala Lumpur |   Singapore |\n|-------:|-----------:|---------:|------------:|---------------:|------------:|\n|   2010 |     288997 | 145527   |      404735 |       226787   |      529407 |\n|   2011 |     304628 | 169868   |      428990 |       244053   |      583921 |\n|   2012 |     312828 | 259444   |      400596 |       272093   |      614155 |\n|   2013 |     306783 | 257263   |      353895 |       272804   |      592886 |\n|   2014 |     309318 | 244776   |      330521 |       261438   |      620419 |\n|   2015 |     286202 | 263378   |      290292 |       252906   |      633862 |\n|   2016 |     285973 | 236419   |      309556 |       175858   |      614172 |\n|   2017 |     314405 | 226048   |      340216 |       199868   |      662505 |\n|   2018 |     126712 |  91611.2 |      134540 |        74667.5 |      250653 |\n```\n\nSave the table as a csv:\n\n```python\npivot.save_csv("2010s_freight_sources_top5.csv")\n```\n\n## Design philosophy\n\n- Avoid boilerplate at all costs. Make it as simple as possible but no simpler.\n\n- Don\'t reinvent the wheel: `results` uses sqlalchemy for database connections, existing excel parsing libraries for excel parsing, etc etc. `results` brings it all together, sprinkles some sugar on top, and puts it at your fingertips.\n\n- Eat your own dogfood: We use this ourselves every day.\n\n## Documentation\n\nThis README.md is currently all there is :( But we\'ll add more soon, we promise!\n\n## Credits\n\n- [Rob](https://github.com/djrobstep)\n- [Jason](https://github.com/jasongi)\n- [Nick](https://github.com/nmcl23)\n\n## Contributions\n\nYes please!\n',
    'author': 'Robert Lechte',
    'author_email': 'rlechte@actu.org.au',
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'python_requires': '>=3.7',
}


setup(**setup_kwargs)
