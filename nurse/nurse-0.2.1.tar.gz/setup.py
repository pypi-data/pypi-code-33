# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['nurse']

package_data = \
{'': ['*']}

setup_kwargs = {
    'name': 'nurse',
    'version': '0.2.1',
    'description': 'A thoughtful dependency injection framework 💉',
    'long_description': 'Nurse\n=====\n\n.. image:: https://img.shields.io/badge/license-public%20domain-ff69b4.svg\n    :target: https://github.com/ZeroGachis/nurse#license\n\n\n.. image:: https://img.shields.io/badge/pypi-v0.2.1-blue.svg\n    :target: https://pypi.org/project/nurse/\n\n\nOutline\n~~~~~~~\n\n1. `Overview <https://github.com/ZeroGachis/nurse#overview>`_\n2. `Installation <https://github.com/ZeroGachis/nurse#installation>`_\n3. `Usage <https://github.com/ZeroGachis/nurse#usage>`_\n4. `License <https://github.com/ZeroGachis/nurse#license>`_\n\n\nOverview\n~~~~~~~~\n\n\n**Nurse** is a **dependency injection framework** with a small API that uses\ntype annotations to manage dependencies in your codebase.\n\n\nInstallation\n~~~~~~~~~~~~\n\n**Nurse** is a Python3-only module that you can install via `Poetry <https://github.com/sdispater/poetry>`_\n\n.. code:: sh\n\n    poetry add nurse\n\n\nIt can also be installed with `pip`\n.. code:: sh\n\n    pip3 install nurse\n\n\nUsage\n~~~~~\n\n**Nurse** stores the available dependencies into a service catalog, that needs to be\nfilled-in generally at the startup of your application.\n\n.. code:: python3\n\n    import nurse\n    \n    # A user defined class that will be used accross your application\n    class SSHClient:\n        \n        def user(self) -> str:\n            return "John Doe"\n    \n    # Now, add it to nurse service catalog in order to use it later in your application\n    nurse.serve(SSHClient())\n\n\nOnce you filled-in the service catalog with your different component, your can declare them as dependencies\nto any of your class.\n\n.. code:: python3\n\n    import nurse\n\n    @nurse.inject\n    class Server:\n        ssh_client: SSHClient\n\n        def response(self) -> str:\n            return f"Hello {self.ssh_client.user()} !"\n    \n\n    server = Server()\n    server.response()\n    # Hello John Doe !\n\n\nLicense\n~~~~~~~\n\n**Nurse** is released into the Public Domain. ðŸŽ‰\n',
    'author': 'ducdetronquito',
    'author_email': 'g.paulet@zero-gachis.com',
    'url': 'https://github.com/ZeroGachis/nurse',
    'packages': packages,
    'package_data': package_data,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
