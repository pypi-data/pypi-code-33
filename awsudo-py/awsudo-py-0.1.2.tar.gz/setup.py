# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['awsudo_py']

package_data = \
{'': ['*']}

install_requires = \
['boto3>=1.9,<2.0', 'botocore>=1.12,<2.0']

entry_points = \
{'console_scripts': ['awsudo = awsudo_py.awsudo:main']}

setup_kwargs = {
    'name': 'awsudo-py',
    'version': '0.1.2',
    'description': 'A sudo-like tool to configure AWS environment variables and call programs',
    'long_description': "# awsudo [![CircleCI](https://circleci.com/gh/chdsbd/awsudo-py.svg?style=svg)](https://circleci.com/gh/chdsbd/awsudo-py) [![pypi](https://img.shields.io/pypi/v/awsudo-py.svg)](https://pypi.org/project/awsudo-py/)\n> A sudo-like tool to configure AWS environment variables and call programs\n\nThis script is useful for programs like Terraform, which doesn't support MFA when assuming roles. \n\n\n## Installation\n```sh\npython3 -m pip install awsudo-py\n```\n\n## Usage\n```console\n$ awsudo -p administrator@staging terraform apply\n\n$ awsudo -p administrator@staging env | grep AWS\nAWS_ACCESS_KEY_ID=AKIAIXMBKCITA257EHIQ\nAWS_SECRET_ACCESS_KEY=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\n```\n\n```\nusage: awsudo [-h] [-p PROFILE] PROG [ARG [ARG ...]]\n\nSet environment variables using profile\n\npositional arguments:\n  PROG                  executable to run\n  ARG                   args to run with program\n\noptional arguments:\n  -h, --help            show this help message and exit\n  -p PROFILE, --profile PROFILE\n                        AWS Profile to assume\n```\n\n## Development\n[Poetry][poetry] is necessary to install this project for development.\n```sh\n# install dependencies\nmake install\n\n# linting\nmake typecheck\nmake fmt\n# error on bad formatting\nmake fmt-check\nmake lint\n\n# testing\nmake test\n# runs fmt, typecheck, build\nmake all \n\n# building/publishing\nmake clean\nmake build\nmake publish\n# build and install program directly\nmake install-program\nmake uninstall-program\n\n# run program (we can't pass args to Make)\npoetry run awsudo\n```\n[poetry]: https://github.com/sdispater/poetry\n\n## Prior Art\nThere are a lot of similar programs to this one. I believe [makethunder/awsudo][0] and [electronicarts/awsudo][1] are the best alternatives. The only problems with [makethunder/awsudo][0] are that it isn't published on pypi and that it doesn't use the newest api for caching sessions. [electronicarts/awsudo][1] has all of the features, but it uses an internal session cache, instead of sharing with awscli. If you need SAML support though, the internal cache is a necessary compromise, so this package is great in that case.\n\nproject|awscli profiles|session caching|SAML|language|published\n---|---|---|---|---|---\nthis project|yes|yes|no|python3.6|pypi\n[makethunder/awsudo][0]|yes|yes*|no|python|github\n[electronicarts/awsudo][1]|yes|yes⦿|yes|ruby|rubygems\n[pmuller/awsudo][2]|yes|no|no|python2.7, python3.5|pypi\n[ingenieux/awsudo][3]|no|no|no|golang|no\n[meltwater/awsudo][4]|yes|yes|no|bash, node|npm, dockerhub\n\n\\*  supports session caching through older technique using awscli as a dependency\n\n⦿ uses a daemon to cache sessions internally\n\n[0]: https://github.com/makethunder/awsudo\n[1]: https://github.com/electronicarts/awsudo\n[2]: https://github.com/pmuller/awsudo\n[3]: https://github.com/ingenieux/awsudo\n[4]: https://github.com/meltwater/awsudo\n",
    'author': 'Christopher Dignam',
    'author_email': 'chris@dignam.xyz',
    'url': 'https://github.com/chdsbd/awsudo-py',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.6.5,<4.0.0',
}


setup(**setup_kwargs)
