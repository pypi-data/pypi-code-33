# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['pyramid_marshmallow']

package_data = \
{'': ['*'], 'pyramid_marshmallow': ['assets/*']}

install_requires = \
['marshmallow>=2.16,<3.0', 'pyramid>=1.7,<2.0']

extras_require = \
{'openapi': ['apispec>=0.37,<0.38', 'PyYAML>=3.10,<4.0']}

entry_points = \
{'console_scripts': ['generate-spec = '
                     'pyramid_marshmallow.generatespec:generate']}

setup_kwargs = {
    'name': 'pyramid-marshmallow',
    'version': '0.4.1',
    'description': 'Validate request and response data with Marshmallow and optionally generate an OpenAPI spec.',
    'long_description': '# pyramid-marshmallow\n\npyramid-marshmallow is a simple Pyramid plugin that allows you to validate and\nmarshal a JSON HTTP request or response using\n[Marshmallow](http://marshmallow.readthedocs.io/) schemas.  You can then\nleverage this to automatically generate an OpenAPI specification for your API.\n\n## Basic usage\n\nInstall the project with `pip install pyramid-marshmallow`.\n\nActivate it by adding `config.include(\'pyramid_marshmallow\')` into your config\nfunction or adding `pyramid.includes = pyramid_marshmallow` into your ini file.\n\nTo validate incoming data, set `validate` to a Marshmallow schema in your\n`view_config`.  The request body is parsed as JSON then passed through the\nschema\'s `load` function.  You can access the processed data with\n`request.data`.\n\n```python\nfrom marshmallow import Schema, String\n\n\nclass HelloSchema(Schema):\n    name = String()\n\n\n@view_config(\n    context=Root,\n    name=\'hello\',\n    request_method=\'post\',\n    validate=HelloSchema(),\n)\ndef hello(context, request):\n    return Response(body=\'Hello, {}\'.format(\n        request.data[\'name\']\n    ))\n```\n\nFor GET requests, the URL parameters are passed into the schema.  Value lists\nare not currently supported.\n\nSetting `marshal` in your `view_config` will run the view output through\nmarshmallow (i.e. `Schema.dump`) before going to the renderer.  You probably\nwill want to set the renderer to `json`.\n\n```\n@view_config(\n    context=Root,\n    name=\'hello\',\n    request_method=\'get\',\n    marshal=HelloSchema(),\n    renderer=\'json\',\n)\ndef hello(context, request):\n    name = fetch_name()\n    return {\n        \'name\': name,\n    }\n```\n\n`validate` and `marshal` operate independently, so can be used separately or\ntogether.\n\nAs a convenience, you can pass in a dictionary to `validate` or `marshal` and\npyramid-marshmallow will turn it into a schema for you.\n\n```python\n@view_config(\n    context=Root,\n    name=\'hello\',\n    request_method=\'post\',\n    validate={\n        \'name\': String(),\n    },\n)\n```\n\nYou can also get a schema made from a dictionary by using the\n`pyramid_marshmallow.make_schema` function.  This can be useful for `Nested`\nfields.\n\n\n### Error handling\n\nIf the validation fails, a `pyramid_marshmallow.ValidationError` is raised.\nThe `errors` property of the exception contains a dictionary of error messages,\njust like the `Schema.load` method returns.\n\nYou may want to attach a view to this exception to expose the error messages to\nthe user.\n\n```python\n@view_config(\n    context=ValidationError,\n    renderer=\'json\',\n)\ndef validation_error(context, request):\n    request.response.status = 401  # HTTP Bad Request\n    return {\n        \'errors\': context.errors,\n    }\n```\n\nA failure during marshalling will result in a\n`pyramid_marshmallow.MarshalError` which behaves in the same manner.  It\'s\nusually less useful to attach a view to that exception, since marshalling\nerrors are usually not encountered during standard operation.\n\n## OpenAPI\n\nBy adding validation and marshalling to your views, we have the opportunity to\nutilize that data to generate documentation.  pyramid-marshmallow includes an\nutility that uses [apispec](https://apispec.readthedocs.io/en/stable/) to\ngenerate an [OpenAPI](https://swagger.io/resources/open-api/) specification for\nyour application.\n\nFirst, you\'ll need to install some extra dependencies.\n\n```bash\npip install pyramid-marshmallow[openapi]\n```\n\nNow you can generate your spec by simply passing in an ini file.\npyramid-marshmallow needs to run your application in order to inspect it, so\nthe ini file should contain all the necessary configuration to do so.\n\n```bash\ngenerate-spec development.ini\n```\n\nThis will output the spec to stdout as JSON.  You can set the `--output` flag\nto output the results to a file.\n\nYou can set `--format yaml` to output the spec as YAML instead or\n`--format zip` to output a zip file containing the spec and\n[Swagger UI](https://swagger.io/tools/swagger-ui/), a web interface for viewing\nthe spec.\n\nBy default, your spec will be titled "Untitled" and versioned "0.1.0".  You can\nchange this by setting `openapi.title` and `openapi.version` in your ini file.\n\n### Additional Documentation\n\nTo add additional documentation to schema fields, you can set the `description`\nproperty.\n\n```python\nclass Hello(Schema):\n    name = String(required=True, description=\'Your first and last name.\')\n```\n\nDocumentation for the endpoint will be pulled from the view callable\'s\ndocstring.\n\nYou can also augment the spec by adding a line of three hyphens followed by\nYAML.  The YAML will be parsed and merged into to the endpoint\'s spec.  This\ncan be useful for documenting endpoints that cannot be validated or marshalled,\nsuch as endpoints that return an empty body.\n\n```python\n@view_config(\n    context=WidgetResource,\n    method=\'post\',\n    validate=WidgetSchema(),\n)\ndef create_widget(context, request):\n    """\n    Create a new widget.\n    ---\n    responses:\n        201:\n            description: Indicates the widget was successfully created.\n    """\n    create_widget()\n    return HTTPCreated()\n```\n\n## URL Traversal\n\nIf you\'re using Pyramid\'s URL traversal, the generated spec may be mostly\nempty.  This is because pyramid-marshmallow has no way of knowing where in the\nresource tree a resource is.  You can denote this by setting the `__path__`\nproperty on each resource.\n\n```python\nclass Widget(Resource):\n    __path__ = \'/widget\'\n```\n\nViews attached to this resource will then be added to the spec.\n\nYou can add parameters to your path via the `__params__` property.  You can\nalso tag all attached views via `__tag__`.  Once you define a tag in one\nresource, you can use it elsewhere by setting `__tag__` to the tag name.\n\n```python\nclass Widget(Resource):\n    __path__ = \'/widget/{widgetId}\'\n    __params__ = [{\n        \'name\': \'widgetId\',\n        \'schema\': {\n            \'type\': \'integer\',\n        },\n    }]\n    __tag__ = {\n        \'name\': \'widgets\',\n        \'description\': \'Endpoints for managing a widget.\',\n    }\n```\n\n',
    'author': 'Theron Luhn',
    'author_email': 'theron@luhn.com',
    'url': 'https://github.com/luhn/pyramid-marshmallow',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'entry_points': entry_points,
    'python_requires': '>=3.4,<4.0',
}


setup(**setup_kwargs)
