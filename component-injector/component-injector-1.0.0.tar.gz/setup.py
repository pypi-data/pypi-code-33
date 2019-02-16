# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['component_injector']

package_data = \
{'': ['*']}

extras_require = \
{':python_version < "3.7"': ['contextvars>=2.3,<3.0']}

setup_kwargs = {
    'name': 'component-injector',
    'version': '1.0.0',
    'description': 'A modern component / dependency injector for python 3.6+.',
    'long_description': "# component-injector\n> A modern component / dependency injector for python 3.6+.\n\nThis library provides a framework-agnostic component (or dependency)\ninjector that injects registered components into your function calls.\nThe components to insert are identified by looking at the called\nfunction argument annotations.\n\nWhen registering a component, all its base classes are registered as\nwell unless you explicitly disable that. You can also choose to only\nregister base classes that are not already registered with the\ninjector.\n\nIt provides local scopes where you can register additional components\nor override existing components. After exiting the scope, the registry\nwill return to the state it was in before entering the scope.\n\n## Compatibility\n\n`component-injector` is compatible with python 3.6+ using the\nbackported `contextvars` package.\n\nThe scopes are thread-safe and when using python 3.7 also safe for for\nuse with asyncio tasks.\n\n## Installation\n\n`component-injector` is available from pypi:\n\n```sh\npip install component-injector\n```\n\n## Usage example\n\nHere's a small demo on how to use the injector:\n\n```\nfrom component_injector import Injector\n\ninjector = Injector()\n\nclass O:\n    pass\n\n@injector.inject\ndef consumer_of_o(o: O) -> None:\n    print(o)\n\ninjector.register(O())\nconsumer_of_o()  # 'o' wil be the registered instance.\n\nconsumer_of_o(O())  # 'o' will be this new instance.\n```\n\n_For more examples and usage, please refer to\n[demo.py](https://github.com/iksteen/component_injector/blob/master/demo.py)\nand\n[async_demo.py](https://github.com/iksteen/component_injector/blob/master/async_demo.py)._\n\n## Development setup\n\nFor development purposes, you can clone the repository and use\n[poetry](https://poetry.eustace.io/) to install and maintain the\ndependencies. There is no test suite. The project comes with a set of\npre-commit hooks that can format (isort, black) and check your code\n(mypy, flake8) automatically.\n\n```sh\ngit clone git@github.com:iksteen/component-injector.git\ncd component-injector\npoetry run pre-commit install\n```\n\n## Release History\n\n* 1.0.0\n    * Initial Release.\n\n## Meta\n\nIngmar Steen – [@iksteen](https://twitter.com/iksteen)\n\nDistributed under the MIT license. See ``LICENSE`` for more information.\n\n[https://github.com/iksteen/](https://github.com/iksteen/)\n\n## Contributing\n\n1. Fork it (<https://github.com/iksteen/component-injector/fork>)\n2. Create your feature branch (`git checkout -b feature/fooBar`)\n3. Commit your changes (`git commit -am 'Add some fooBar'`)\n4. Push to the branch (`git push origin feature/fooBar`)\n5. Create a new Pull Request\n",
    'author': 'Ingmar Steen',
    'author_email': 'iksteen@gmail.com',
    'url': 'https://www.github.com/iksteen/component-injector',
    'packages': packages,
    'package_data': package_data,
    'extras_require': extras_require,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
