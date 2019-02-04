# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['dbplot']

package_data = \
{'': ['*']}

install_requires = \
['ibis-framework>=0.14,<0.15', 'matplotlib>=3.0,<4.0']

setup_kwargs = {
    'name': 'dbplot',
    'version': '0.1.0',
    'description': 'dbplot allows you to make calculations of plots inside databases',
    'long_description': '# dbplot\n\ndbplot allows you to make calculations for plots inside databases.\n\ndbplot is powered by [ibis](https://github.com/ibis-project/ibis) so its possible to target multiple databases that include:\nPostgres, MySQL, Apache Impala, Apache Kudu, BigQuery [and more](https://docs.ibis-project.org/), also everything that ibis will support\nin the future such as Apache Spark.\n\n## Install\n\n```\npip install dbplot\n```\n\nDevelopment version:\n\n```\npip install git+git://github.com/danielfrg/dbplot.git\n```\n\n## Usage\n\nSee [notebooks]() for examples.\n\n```python\nimport os\nimport ibis\nimport dbplot\n\n# Connect to DB\nhost = os.environ.get("DBPLOT_TEST_POSTGRES_HOST", "localhost")\nuser = os.environ.get("DBPLOT_TEST_POSTGRES_USER", "postgres")\npassword = os.environ.get("DBPLOT_TEST_POSTGRES_PASSWORD")\ndatabase = os.environ.get("DBPLOT_TEST_POSTGRES_DATABASE", "nycflights13")\ncon = ibis.postgres.connect(host=host, database=database, user=user, password=password)\n\n# Get a table\nflights = con.table("flights")\n\n# Plot stuff\ndbplot.hist(flights, flights.dep_time, nbins=20)\n```\n\n## Roadmap\n\n- Automated tests\n- More plots such as raster plots, line charts and more :)\n\n## Notes\n\nBased on [dbplot for R](https://github.com/edgararuiz/dbplot).\n',
    'author': 'Daniel Rodriguez',
    'author_email': 'df.rodriguez143@gmail.com',
    'url': 'https://github.com/danielfrg/dbplot',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.5,<4.0',
}


setup(**setup_kwargs)
