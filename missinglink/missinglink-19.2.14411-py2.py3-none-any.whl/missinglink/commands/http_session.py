# -*- coding: utf8 -*-
from missinglink.commands.mali_version import get_missinglink_cli_version


def create_http_session():
    import requests

    session = requests.session()

    session.headers.update({'User-Agent': 'ml_cli/{}'.format(get_missinglink_cli_version())})

    return session
