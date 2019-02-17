# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['cnab']

package_data = \
{'': ['*']}

install_requires = \
['canonicaljson>=1.1,<2.0']

extras_require = \
{'docker': ['docker>=3.6,<4.0']}

setup_kwargs = {
    'name': 'cnab',
    'version': '0.1.7',
    'description': 'A module for working with Cloud Native Application Bundles in Python',
    'long_description': '# Python CNAB Library\n\n_Work-in-progress_ library for working with [CNAB](https://cnab.io/) in Python.\n\nThere are probably three main areas of interest for a CNAB client:\n\n1. Handling the `bundle.json` format ([101](https://github.com/deislabs/cnab-spec/blob/master/101-bundle-json.md))\n2. Building invocation images ([102](https://github.com/deislabs/cnab-spec/blob/master/102-invocation-image.md))\n3. Running actions against a CNAB ([103](https://github.com/deislabs/cnab-spec/blob/master/103-bundle-runtime.md))\n\nClaims and Signing are optional but will be worked on once the above are stable.\n\n\n## Installation\n\nThe module is published on [PyPi](https://pypi.org/project/cnab/) and can be installed from there.\n\n```bash\npip install cnab\n```\n\n\n## Parsing `bundle.json`\n\nNothing too fancy here, the `Bundle` class  has a `from_dict` static method which\nbuilds a full `Bundle` object.\n\n```python\nimport json\nfrom cnab import Bundle\n\nwith open("bundle.json") as f:\n    data = json.load(f)\n\nbundle = Bundle.from_dict(data)\n```\n\nThis could for example be used for validation purposes, or for building user interfaces for `bundle.json` files.\n\n\n## Describing `bundle.json` in Python \n\nYou can also describe the `bundle.json` file in Python. This will correctly validate the\nstructure based on the current specification and would allow for building a custom DSL or other\nuser interface for generating `bundle.json` files.\n\n```python\nfrom cnab import Bundle, InvocationImage\n\nbundle = Bundle(\n    name="hello",\n    version="0.1.0",\n    invocation_images=[\n        InvocationImage(\n            image_type="docker",\n            image="technosophos/helloworld:0.1.0",\n            digest="sha256:aaaaaaa...",\n        )\n    ],\n)\n\nprint(bundle.to_json())\n```\n\n## Running CNABs\n\nThe module supports running actions on a CNAB, using the `docker` driver.\n\n```python\nfrom cnab import CNAB\n\n# The first argument can be a path to a bundle.json file, a dictionary\n# or a full `Bundle` object\napp = CNAB("fixtures/helloworld/bundle.json")\n\n# list available actions\nprint(app.actions)\n\n# list available parameters\nprint(app.parameter)\n\n# run the install action\nprint(app.run("install"))\n\n# run the install action specifying a parameters\nprint(app.run("install", parameters={"port": 9090}))\n\n# Many applications will require credentials\napp = CNAB("fixtures/hellohelm/bundle.json")\n\n# list required credentials\nprint(app.credentials)\n\n# Here we pass the value for the required credential\n# in this case by reading the existing configuration from disk\nwith open("/home/garethr/.kube/config") as f:\n    print(app.run("status", credentials={"kubeconfig": f.read()}))\n```\n\nNote that error handling for this is very work-in-progress.\n\n\n## Working with invocation images\n\n`pycnab` also has a class for working with invocation images.\n\n```python\nfrom cnab import CNABDirectory\n\ndirectory = CNABDirectory("fixtures/invocationimage")\n\n# Check whether the directory is valid\n# Raises `InvalidCNABDirectory` exception if invalid\ndirectory.valid()\n\n# Returns the text of the associated README file if present\ndirectory.readme()\n\n# Returns the text of the associated LICENSE file if present\ndirectory.license()\n```\n\n\n## Thanks\n\nThanks to [QuickType](https://quicktype.io/) for bootstrapping the creation of the Python code for manipulating `bundle.json` based on the current JSON Schema.\n\n',
    'author': 'Gareth Rushgrove',
    'author_email': 'gareth@morethanseven.net',
    'url': 'https://github.com/garethr/pycnab',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
