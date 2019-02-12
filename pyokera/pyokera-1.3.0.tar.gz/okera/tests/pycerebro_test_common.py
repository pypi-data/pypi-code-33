# pylint: disable=bad-continuation
# pylint: disable=bad-indentation
import os

from okera import context

ROOT_TOKEN = os.environ['OKERA_HOME'] + '/integration/tokens/cerebro.token'

identity = lambda x: x

def get_env_var(name, coercer, default):
    if name in os.environ:
        return coercer(os.environ[name])
    return default

def get_test_context():
    auth_mech = get_env_var('PYCEREBRO_TEST_AUTH_MECH', identity, 'NOSASL')
    ctx = context()
    if auth_mech == 'NOSASL':
        ctx.disable_auth()
    elif auth_mech == 'TOKEN':
        ctx.enable_token_auth(token_file=ROOT_TOKEN)
    else:
        assert False
    return ctx

def get_planner(host=None, port=None):
    if host is not None:
        host = host
    else:
        host = get_env_var('PYCEREBRO_TEST_HOST', identity, 'localhost')

    if port is not None:
        port = port
    else:
        port = get_env_var('PYCEREBRO_TEST_PLANNER_PORT', int, 12050)

    return get_test_context().connect(host=host, port=port)

def get_worker(host=None, port=None):
    if host is not None:
        host = host
    else:
        host = get_env_var('PYCEREBRO_TEST_HOST', identity, 'localhost')

    if port is not None:
        port = port
    else:
        port = get_env_var('PYCEREBRO_TEST_WORKER_PORT', int, 13050)

    return get_test_context().connect_worker(host=host, port=port)

def configure_botocore_patch():
    os.environ['OKERA_PATCH_BOTO'] = 'True'
    os.environ['OKERA_PLANNER_HOST'] = 'localhost'
    with open(ROOT_TOKEN, 'r') as token_file:
        os.environ['OKERA_USER_TOKEN'] = token_file.read().strip(' \t\n\r')
    from okera import initialize_default_context, check_and_patch_botocore
    initialize_default_context()
    check_and_patch_botocore()
