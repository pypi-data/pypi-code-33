# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['starlette_api', 'starlette_api.codecs', 'starlette_api.components']

package_data = \
{'': ['*'], 'starlette_api': ['templates/*']}

install_requires = \
['marshmallow>2', 'starlette>=0.9.10']

extras_require = \
{'full': ['apispec>=0.39.0,<0.40.0', 'pyyaml>=3.13,<4.0']}

setup_kwargs = {
    'name': 'starlette-api',
    'version': '0.4.0',
    'description': 'Starlette API layer inherited from APIStar',
    'long_description': '# Starlette API\n[![Build Status](https://travis-ci.org/PeRDy/starlette-api.svg?branch=master)](https://travis-ci.org/PeRDy/starlette-api)\n[![codecov](https://codecov.io/gh/PeRDy/starlette-api/branch/master/graph/badge.svg)](https://codecov.io/gh/PeRDy/starlette-api)\n[![PyPI version](https://badge.fury.io/py/starlette-api.svg)](https://badge.fury.io/py/starlette-api)\n\n* **Version:** 0.4.0\n* **Status:** Production/Stable\n* **Author:** José Antonio Perdiguero López\n\n## Introduction\n\nThat library aims to bring a layer on top of Starlette framework to provide useful mechanism for building APIs. It\'s \nbased on API Star, inheriting some nice ideas like:\n\n* **Schema system** based on [Marshmallow](https://github.com/marshmallow-code/marshmallow/) that allows to **declare**\nthe inputs and outputs of endpoints and provides a reliable way of **validate** data against those schemas.\n* **Dependency Injection** that ease the process of managing parameters needed in endpoints.\n* **Components** as the base of the plugin ecosystem, allowing you to create custom or use those already defined in \nyour endpoints, injected as parameters.\n* **Starlette ASGI** objects like `Request`, `Response`, `Session` and so on are defined as components and ready to be \ninjected in your endpoints.\n* **Auto generated API schema** using OpenAPI standard. It uses the schema system of your endpoints to extract all the \nnecessary information to generate your API Schema.\n* **Auto generated docs** providing a [Swagger UI](https://swagger.io/tools/swagger-ui/) or \n[ReDocs](https://rebilly.github.io/ReDoc/) endpoint.\n\n## Requirements\n\n* Python 3.6+\n* Starlette 0.10+\n\n## Installation\n\n```console\n$ pip install starlette-api\n```\n\n## Example\n\n```python\nfrom marshmallow import Schema, fields, validate\nfrom starlette_api.applications import Starlette\n\n\n# Data Schema\nclass Puppy(Schema):\n    id = fields.Integer()\n    name = fields.String()\n    age = fields.Integer(validate=validate.Range(min=0))\n\n\n# Database\npuppies = [\n    {"id": 1, "name": "Canna", "age": 6},\n    {"id": 2, "name": "Sandy", "age": 12},\n]\n\n\n# Application\napp = Starlette(\n    components=[],      # Without custom components\n    title="Foo",        # API title\n    version="0.1",      # API version\n    description="Bar",  # API description\n    schema="/schema/",  # Path to expose OpenAPI schema\n    docs="/docs/",      # Path to expose Swagger UI docs\n    redoc="/redoc/",    # Path to expose ReDoc docs\n)\n\n\n# Views\n@app.route("/", methods=["GET"])\ndef list_puppies(name: str = None) -> Puppy(many=True):\n    """\n    List the puppies collection. There is an optional query parameter that \n    specifies a name for filtering the collection based on it.\n    \n    Request example:\n    GET http://example.com/?name=Sandy\n    \n    Response example:\n    200\n    [\n        {"id": 2, "name": "Sandy", "age": 12}\n    ]\n    """\n    return [puppy for puppy in puppies if puppy["name"] == name]\n    \n\n@app.route("/", methods=["POST"])\ndef create_puppy(puppy: Puppy) -> Puppy:\n    """\n    Create a new puppy using data validated from request body and add it\n    to the collection.\n    \n    Request example:\n    POST http://example.com/\n    {\n        "id": 1,\n        "name": "Canna",\n        "age": 6\n    }\n    \n    Response example:\n    200\n    {\n        "id": 1,\n        "name": "Canna",\n        "age": 6\n    }\n    """\n    puppies.append(puppy)\n    \n    return puppy\n```\n\n## Credits\n\nThat library started mainly as extracted pieces from [APIStar](https://github.com/encode/apistar) and adapted to work \nwith [Starlette](https://github.com/encode/starlette).\n\n## Contributing\n\nThis project is absolutely open to contributions so if you have a nice idea, create an issue to let the community \ndiscuss it.',
    'author': 'José Antonio Perdiguero López',
    'author_email': 'perdy@perdy.io',
    'url': 'https://github.com/PeRDy/starlette-api',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
