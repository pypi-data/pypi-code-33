# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['lhclient']

package_data = \
{'': ['*']}

install_requires = \
['click>=7.0,<7.1', 'requests[security]>=2.18.4,<2.19.0']

entry_points = \
{'console_scripts': ['lhclient = lhclient:cli']}

setup_kwargs = {
    'name': 'lhclient',
    'version': '0.1.14',
    'description': 'The official client for the Logichub API',
    'long_description': "# lhclient\n\nThis utility connects to a deployment to\n\n* Import scripts\n* Import modules\n* Import flow\n* Create an Event Type from a CSV file\n\n## Parameters\n\nAll actions expect the following parameters\n\n* origin: eg. https://<yourdeployment>/api\n* username\n* password (prompted interactively if missing)\n\nThe last argument is either a file or a directory. If a directory is provided, the script will apply the action to all the files in the directory with suffixes .json, .py, .sh, .csv.\n\n## Actions\n\n### Import a script\n\nUploads either a python or a bash script. If a script with the same name already exists, its contents are overwritten with the new contents (that's how the backend works, nothing specific to this script).\n\n#### Syntax\n\n```\npython lhclient.py import script --origin https://<deployment_host>/api --username <username> <the py/sh file or folder>\n```\n\n### Import a module\n\nImports a module from its JSON representation. If a module with the same ID already exists, it will fail with the `DuplicateModuleIdException` exception. \n\n#### Syntax\n\n```\npython lhclient.py import module --origin https://<deployment_host>/api --username <username> <the json file or folder>\n```\n\n### Import a flow\n\nImports a flow from its JSON representation. We are currently using the legacy API, so import will fail if a flow with the same name already exists.\n\n#### Syntax\n\n```\npython lhclient.py import flow --origin https://<deployment_host>/api --username <username> <the json file or folder>\n```\n\n### Create Event Type from CSV\n\nUploads a CSV file, creates a new FileConnection (named as the file, without the extension) and creates a new EventType (named as the file, without the extension as well). If the CSV file already exists, its contents will NOT be overwritten on the server. If an EventType already has the name of the filename, the creation will fail (we can't have two EventTypes with the same name).\n\nYou can optionally use the --name argument to specify the name to use for both the FileConnection and the EventType\n\n#### Syntax\n\n```\npython lhclient.py create event-type from-csv --origin https://<deployment_host>/api --username <username> <the csv file or folder>\n```\n",
    'author': 'William Le Ferrand',
    'author_email': 'william@logichub.com',
    'url': 'https://logichub.com',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=2.7, !=3.0.*, !=3.1.*, !=3.2.*, !=3.3.*',
}


setup(**setup_kwargs)
