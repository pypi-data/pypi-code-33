# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['create_tomochain_masternode', 'create_tomochain_masternode.templates']

package_data = \
{'': ['*']}

install_requires = \
['click>=7.0,<8.0', 'jinja2>=2.10,<3.0', 'pyyaml>=3.13,<4.0']

entry_points = \
{'console_scripts': ['create-tomochain-masternode = '
                     'create_tomochain_masternode.main:entrypoint']}

setup_kwargs = {
    'name': 'create-tomochain-masternode',
    'version': '1.0.0',
    'description': 'Set up a TomoChain masternode by running one command.',
    'long_description': '# create-tomochain-masternode\nSet up a TomoChain masternode by running one command.\n\n## Installation\n\nRequires:\n- Docker\n- Docker-compose\n\n### Binary\n\nDownload `create-tomochain-masternode` from the [latest release](https://github.com/tomochain/create-tomochain-masternode/releases/latest).\n\n```bash\nchmod +x create-tomochain-masternode\nmv create-tomochain-masternode /usr/local/bin/\n```\n\n### Pypi\n\nRequires Python >= 3.6.\n\n```bash\npip3 install --user create-tomochain-masternode\n```\n\n## Usage\n\n```\nUsage: create-tomochain-masternode [OPTIONS] NAME\n\n  Set up a TomoChain masternode by running one command.\n\nOptions:\n  --testnet  Testnet instead of mainnet.\n  --version  Show the version and exit.\n  --help     Show this message and exit.\n```\n\nSimply run create-tomochain-masternode with the name of your masternode as arguemnt `NAME`.\n\n```bash\ncreate-tomochain-masternode tomochain09\n```\n\nFollow the wizard by replying to the following questions:\n- **Coinbase private key**:\n  Your masternode coinbase account private key.\n  This is the account you configured your masternode with, not the one holding your funds.\n- **Storage**:\n  Either `docker volume` if you want to use one, or `host directory` if you want to bind mount a specific location of your filesystem.\n- **Chaindata**:\n  The name of the docker volume that will be used, or the path to the directory to bind mount, depending on your choice to the last question.\n- **Expose RPC**:\n  If you want to expose or not port `8545`.\n  It is the RPC api to your node.\n  It should be only exposed if you have a specific reason to do so.\n  The masternode owner is responsible of proxing and securing the RPC api as it should not be directly exposed to the internet.\n- **Expose WebSocket**:\n  If you want to expose or not port `8546`.\n  It is the WebSocket api to your node.\n  It should be only exposed if you have a specific reason to do so.\n  The masternode owner is responsible of proxing and securing the WebSocket api as it should not be directly exposed to the internet.\n- **Loging level**:\n  Set the logging level of the TomoChain container to error, info or debug.\n  Info or Error is usually a good logging level.\n  Only use the debug level if you a good reason, it will generate a lot of output.\n\nOnce finished, you will get a folder named after your masternode (in our case "tomochain09") with two files.\n\n`docker-compose.yml` which contains the instructions for docker compose to know how to configure your masternode container.\n\n`.env` which contains the configuration made from your answers to the question.\n\nNow that we have docker-compose configured to run our node, we just need to start it.\n\n```bash\ndocker-compose up -d\n```\n\nYou can check that your masternode is running with the `ps` sub-command.\n\n```bash\ndocker-compose ps\n```\n',
    'author': 'etienne-napoleone',
    'author_email': 'etienne@tomochain.com',
    'url': 'https://tomochain.com',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.5,<4.0',
}


setup(**setup_kwargs)
