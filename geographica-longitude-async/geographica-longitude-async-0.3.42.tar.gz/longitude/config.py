"""
Entry point for app configuration. Any module requiring a configuration
parameter should import it from this module.

The module defines a series of basic configuration attributes (listed in
_BASE_CONFIG_PARAMS) whose value will be retrieved from the system
environment. Of these values, only SECRET_KEY is compulsory.

The module then tries to import the global module "settings". This module
should include a
"""

import sys
import pgpy
import os
import configparser
import re

from itertools import chain

from longitude.validators import min_value, max_value, choices_in
from longitude.utils import chain_fns

from .utils import try_or_none, compile_spec, try_list

try:
    import settings

    user_config = []

    # Try to discover enabled modules via alembic plugin_migrations
    settings_path = os.path.join(os.path.dirname(settings.__file__), 'alembic.ini')

    if os.path.exists(settings_path):
        alembic_config = configparser.ConfigParser()
        alembic_config.read(settings_path)

        try:
            plugin_migrations = alembic_config['alembic']['plugin_migrations']
        except KeyError:
            plugin_migrations = ''

        if not plugin_migrations.strip():
            plugin_migrations = []
        else:
            plugin_migrations = re.split('\s+', plugin_migrations)

        plugin_migrations = (
            x
            for x
            in plugin_migrations
            if x.startswith('longitude.')
        )

        for plugin_name in plugin_migrations:
            user_config.append(
                (plugin_name.replace('.', '_').upper() + '_PLUGIN_ENABLED', bool, '1')
            )

    # Add the user config
    user_config.extend(settings.config)

except ImportError:
    user_config = []


_BASE_CONFIG_PARAMS = [
    #(<CONF_NAME>, <CONF_TYPE>, <CONF_DEFAULT_VALUE>)
    ('LONGITUDE_AUTH_PLUGIN_USER_MODEL', str, ''),
    ('LONGITUDE_AUTH_PLUGIN_ENABLED', bool, 0),
    ('LONGITUDE_CREDENTIAL_PLUGIN_ENABLED', bool, 0),
    ('LONGITUDE_PERMISSION_PLUGIN_ENABLED', bool, 0),

    ('LONGITUDE_AUTH_MICROSOFT_CLIENT_SECRET', str, ''),
    ('LONGITUDE_AUTH_MICROSOFT_CLIENT_ID', str, ''),
    ('LONGITUDE_AUTH_MICROSOFT_CLIENT_TENANT', str, ''),

    ('CARTO_API_KEY', str, ''),
    ('CARTO_USER', str, ''),

    ('DB_NAME', str, 'postgres'),
    ('DB_USER', str, 'postgres'),
    ('DB_PASSWORD', str, 'postgres'),
    ('DB_HOST', str, 'postgis'),
    ('DB_PORT', int, 5432),
    ('DB_SCHEMA', str, 'public'),

    ('MAIL_HOSTNAME', str, ''),
    ('MAIL_PORT', int, 25),
    ('MAIL_TIMEOUT', int, 60),
    ('MAIL_USERNAME', str, ''),
    ('MAIL_PASSWORD,', str, ''),
    ('MAIL_FROM_DEFAULT', str, 'example@example.com'),
    # ('MAIL_AUTH_TYPE', chain_fns(str, choices_in(('none', 'plain', 'login', 'crammd5'))), 'none'),
    ('MAIL_USE_TLS', bool, 0),

    ('REDIS_HOST', str, 'redis'),
    ('REDIS_PORT', int, 6379),
    ('REDIS_DB', int, 0),

    ('DEBUG', bool, '1'),
    ('LOG_LEVEL', str, 'INFO'),
    ('WORKERS', int, 1),

    ('CACHE', bool, '1'),
    # Expire time in seconds (default 15 minutes): 15*60=900
    ('CACHE_EXPIRE', int, 900),

    ('SECRET_KEY', str, None),

    ('PAGINATION_MAX_PAGE_SIZE', try_or_none(chain_fns(int, min_value(1), max_value(10000)), allow=ValueError), 10),
    ('PAGINATION_PAGE_SIZE', try_or_none(chain_fns(int, min_value(1), max_value(10000)), allow=ValueError), 10),

    # Default for Sanic-jwt, see http://sanic-jwt.readthedocs.io/en/latest/pages/configuration.html#expiration-delta
    ('API_TOKEN_EXPIRATION', int, 60 * 5 * 6),
    ('AUTH_TOKEN_DOBLE_CHECK', bool, False),
    ('AUTH_USER_TABLE', str, 'users'),
    ('AUTH_TOKEN_TABLE', str, 'users_token'),
    ('TIMEZONE', str, 'Europe/Madrid'),

    ('PGP_PRIVATE_KEY', try_or_none(pgpy.PGPKey.from_file), ''),

    # Credentials module configuration
    ('CREDENTIALS_TYPES', try_list(str), [])
]

_module = sys.modules[__name__]


def fail_required(name):
    raise RuntimeError('Missing required environment var: ' + name)


CONFIG_SPEC = compile_spec(
    spec=chain(_BASE_CONFIG_PARAMS, user_config),
    on_value_success=lambda opt_name, opt_val:
        setattr(_module, opt_name, opt_val),
    on_missing=fail_required,
)

CONFIG_SPEC(os.environ)

