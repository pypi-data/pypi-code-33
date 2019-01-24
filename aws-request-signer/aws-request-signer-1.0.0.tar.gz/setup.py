# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['aws_request_signer']

package_data = \
{'': ['*']}

extras_require = \
{'demo': ['requests>=2.21,<3.0', 'requests_toolbelt>=0.8.0,<0.9.0'],
 'requests': ['requests>=2.21,<3.0']}

setup_kwargs = {
    'name': 'aws-request-signer',
    'version': '1.0.0',
    'description': 'A python library to sign AWS requests using AWS Signature V4.',
    'long_description': '# aws-request-signer\n> A python library to sign AWS requests using AWS Signature V4.\n\nThis small python library serves only purpose: Helping you sign HTTP\nrequests for use with AWS (and compatible) services. The library is\nunopinionated and should work with just about anything that makes HTTP\nrequests (requests, aiohttp).\n\nIt supports generating authorization headers for HTTP requests,\npre-signing URLs so you can easily use them elsewhere and signing S3\nPOST policies for use in HTML forms.\n\nThis library has no requirements, but comes with an authentication\nhelper for the requests package.\n\n## Installation\n\n`aws-request-signer` is available from pypi:\n\n```sh\npip install aws-request-signer\n```\n\n## Usage example\n\nHere\'s an example of how to use the library to sign a request to upload a file to a\n[minio](https://minio.io/) S3 bucket running on your local machine:\n\n```python\nimport hashlib\n\nimport requests\nfrom aws_request_signer import AwsRequestSigner\n\nAWS_REGION = ""\nAWS_ACCESS_KEY_ID = "minio"\nAWS_SECRET_ACCESS_KEY = "minio123"\n\nURL = "http://127.0.0.1:9000/demo/hello_world.txt"\n\n# Demo content for our target file.\ncontent = b"Hello, World!\\n"\ncontent_hash = hashlib.sha256(content).hexdigest()\n\n# Create a request signer instance.\nrequest_signer = AwsRequestSigner(\n    AWS_REGION, AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, "s3"\n)\n\n# The headers we\'ll provide and want to sign.\nheaders = {"Content-Type": "text/plain", "Content-Length": str(len(content))}\n\n# Add the authentication headers.\nheaders.update(\n    request_signer.sign_with_headers("PUT", URL, headers, content_hash)\n)\n\n# Make the request.\nr = requests.put(URL, headers=headers, data=content)\nr.raise_for_status()\n```\n\n_For more examples and usage, please refer to\n[demo.py](https://github.com/iksteen/aws-request-signer/blob/master/demo.py)._\n\n## Development setup\n\nFor development purposes, you can clone the repository and use\n[poetry](https://poetry.eustace.io/) to install and maintain the\ndependencies. There is no test suite. It comes with a set of pre-commit\nhooks that can format (isort, black) and check your code (mypy, flake8)\nautomatically.\n\n```sh\ngit clone git@github.com:iksteen/aws-request-signer.git\ncd aws-request-signer\npoetry install -E demo\npoetry run pre-commit install\n```\n\n**Note**: At the time of writing, the typeshed library that mypy uses\ncontains an incorrect signature for the `requests.auth.AuthBase.__call__`\nmethod. The repository of aws-request-signer includes updated stubs for\nrequests until the signature is fixed upstream.\n\n## Release History\n\n* 1.0.0\n    * Initial Release.\n\n## Meta\n\nIngmar Steen – [@iksteen](https://twitter.com/iksteen)\n\nDistributed under the MIT license. See ``LICENSE`` for more information.\n\n[https://github.com/iksteen/](https://github.com/iksteen/)\n\n## Contributing\n\n1. Fork it (<https://github.com/iksteen/aws-request-signer/fork>)\n2. Create your feature branch (`git checkout -b feature/fooBar`)\n3. Commit your changes (`git commit -am \'Add some fooBar\'`)\n4. Push to the branch (`git push origin feature/fooBar`)\n5. Create a new Pull Request\n',
    'author': 'Ingmar Steen',
    'author_email': 'iksteen@gmail.com',
    'url': 'https://www.github.com/iksteen/aws-request-signer',
    'packages': packages,
    'package_data': package_data,
    'extras_require': extras_require,
    'python_requires': '>=3.5,<4.0',
}


setup(**setup_kwargs)
