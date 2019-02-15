from django.conf import settings

import ldclient


_ld_client = None
_user = None


def init():
    global _ld_client
    global _user
    if _ld_client:
        return
    ldclient.set_config(ldclient.Config(sdk_key=settings.LAUNCHDARKLY_SDK_KEY))
    _ld_client = ldclient.get()
    _user = {"custom": {}, "key": "system", "anonymous": True}


def variation(flag_key: str, default: bool) -> bool:
    init()
    return _ld_client.variation(flag_key, _user, default)
