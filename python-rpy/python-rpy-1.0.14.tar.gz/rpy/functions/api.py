# -*- coding: utf-8 -*-

from __future__ import absolute_import, print_function, unicode_literals

from rpy.functions.encoding import force_bytes
from rpy.functions.importutils import API

pip = API(
    main=('pip.main', 'pip._internal.main'),
    get_installed_distributions=(
        'pip.get_installed_distributions',
        'pip.utils.get_installed_distributions',
        'pip._internal.utils.misc.get_installed_distributions',
    ),
    running_under_virtualenv=(
        'pip.locations.running_under_virtualenv',
        'pip._internal.locations.running_under_virtualenv',
    )
)

base64 = API(
    dumps='base64.b64encode',
    loads='base64.b64decode',
    urlsafe_dumps='base64.urlsafe_b64encode',
    urlsafe_loads='base64.urlsafe_b64decode'
)

json = API(loads='json.loads', dumps='json.dumps')

fernet = API(
    Fernet = 'cryptography.fernet.Fernet',
    loads = lambda payload, password: fernet.Fernet(password).decrypt(payload),
    dumps = lambda payload, password: fernet.Fernet(password).encrypt(force_bytes(payload)),
)

asyncio = API(
    wait = 'asyncio.wait',
    ensure_future = 'asyncio.ensure_future',
    get_event_loop = 'asyncio.get_event_loop',
    new_event_loop = 'asyncio.new_event_loop',
    set_event_loop = 'asyncio.set_event_loop',
)
