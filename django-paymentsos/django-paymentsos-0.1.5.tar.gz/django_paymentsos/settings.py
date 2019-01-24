"""
    This module follows the approach of the JazzBand django apps.

    PAYMENTSOS = {
        'APP_ID': '123',
        'PUBLIC_KEY': '123',
        'PRIVATE_KEY': '123',
    }
"""
from django.conf import settings

USER_SETTINGS = getattr(settings, "PAYMENTSOS", None)

# List of settings that have a default when a value is not provided by the user.
DEFAULTS = {
    'APP_ID': None,
    'PUBLIC_KEY': None,
    'PRIVATE_KEY': None,
    'API_VERSION': '1.2.0',
    'TEST': False,
    'DEBUG': False,
    'REQUESTS_LOGGER': False,
}

# List of settings that cannot be empty
MANDATORY = (
    'APP_ID',
    'PUBLIC_KEY',
    'PRIVATE_KEY',
)


class PaymentsOSSettings(object):
    """
        Settings object that allows accessing the PaymentsOS settings as properties.
    """

    def __init__(self, user_settings=None, defaults=None, mandatory=None):
        self.user_settings = user_settings or {}
        self.defaults = defaults or {}
        self.mandatory = mandatory or {}

    def __getattr__(self, attr):
        if attr not in self.defaults.keys():
            raise AttributeError("Invalid PaymentsOS setting: %r" % (attr))

        try:
            # Check if present in user settings
            val = self.user_settings[attr]
        except KeyError:
            # Fall back to defaults
            val = self.defaults[attr]

        self.validate_setting(attr, val)

        # Cache the result
        setattr(self, attr, val)
        return val

    def validate_setting(self, attr, val):
        if not val and attr in self.mandatory:
            raise AttributeError("PaymentsOS setting: %r is mandatory" % (attr))


paymentsos_settings = PaymentsOSSettings(USER_SETTINGS, DEFAULTS, MANDATORY)
