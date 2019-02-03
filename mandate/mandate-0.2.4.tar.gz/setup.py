# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['mandate', 'mandate.groupobj', 'mandate.userobj', 'mandate.utils']

package_data = \
{'': ['*']}

install_requires = \
['aioboto3',
 'aiohttp',
 'aiohttp-client-manager',
 'asynctest',
 'attrs',
 'envs>=0.3.0',
 'lru-dict',
 'python-jose']

setup_kwargs = {
    'name': 'mandate',
    'version': '0.2.4',
    'description': 'Async wrapper for AWS cognito. Heavily based on capless/warrant',
    'long_description': "# Mandate\n\nAsync fork of [warrant](https://github.com/capless/warrant).\n\nPart of the code was provided by the [warrant](https://github.com/capless/warrant) contributors as part of that software. This code has been duplicated here as allowed by the Apache License 2.0. The warrant code is copyright of the warrant contributors. Any other code is copyright of mandate contributors.\n\n## Initialise\n\n```python\n    cog = Cognito(\n        'pool_id',  # user pool id\n        'client_id',  # client id\n        user_pool_region='eu-west-2', # optional\n        username='your-user@email.com',\n        client_secret='secret', # optional\n        loop=loop # optional\n    )\n```\n\n## Register\n\n```python\n    cog.add_base_attributes(email='your-user@email.com')\n    await cog.register('your-user@email.com', 'password')\n```\n\n`admin_create_user` is also available:\n```python\n    await cog.admin_create_user('user@email.com')\n```\n\n## Confirm Sign up\n\n```python\n    await cog.confirm_sign_up('SIGNUP_CODE', 'your-user@email.com')\n```\n\n`admin_confirm_sign_up` is also available:\n\n```python\n    await cog.admin_confirm_sign_up('user@email.com')\n```\n\n## Authenticate\n\nAll the below examples can be called with or without `admin_` variants.\n\nPer [the documentation](https://docs.aws.amazon.com/en_us/cognito/latest/developerguide/amazon-cognito-user-pools-authentication-flow.html#amazon-cognito-user-pools-server-side-authentication-flow), when running a backend server, you can use the `admin_` methods for authentication and user-related activities. For example:\n\n```python\n    await cog.admin_authenticate(password)\n```\n\nTechnically, the non-admin workflow can also be used with, however I have not got this to work with app secrets! Help would be appreciated here.\n\n```python\n    await cog.authenticate(password)\n```\n\n```\nbotocore.errorfactory.NotAuthorizedException: An error occurred (NotAuthorizedException) when calling the RespondToAuthChallenge operation: Unable to verify secret hash for client <client id>\n```\n\nIf you create an app without app secrets, you should also be able to use the non-admin versions without issues.\n\n## Forgot password\n```python\n    await cog.initiate_forgot_password()\n    # Get the code from the email\n    await cog.confirm_forgot_password(code, new_password)\n```\n\n\n## Get user attributes\n```python\n    await cog.admin_authenticate('password')\n    user = await cog.get_user()\n```\n\n## Change password\n```python\n    await cog.admin_authenticate(old_password)\n    await cog.change_password(old_password, new_password)\n```\n\n## Update profile\n```python\n    await cog.admin_authenticate(password)\n    await cog.admin_update_profile(\n        {\n            'address': 'foo'\n        }\n    )\n```\n\n## Logout\n```python\n    await cog.logout()\n```\n\n## Unit tests\npython -m unittest discover tests\n\n",
    'author': 'Errietta Kostala',
    'author_email': 'errietta@errietta.me',
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
