import conficus

CONFIG = '''
[app]
debug = True

[email]
server = smtp.email.com
user = smtp-admin
password = smtp-password

[email.errors]
to = [admin@email.com]
cc = []

'''


def test_load_defaults():

    config = conficus.load(CONFIG)

    # sanity check
    assert config['app.debug'] is True

    # validate no inheritence
    assert 'server' not in config['email.errors']

    # validate config is readonly
    assert config.readonly is True


def test_read_config(cfg_pth):
    from os import environ
    PATH = str(cfg_pth['config'])
    environ['FICUS_LOAD_PATH_TEST'] = PATH
    with open(PATH, 'r') as fh_:
        CONTENT = fh_.read()

    config_from_path = conficus.read_config(PATH)
    config_from_env_var = conficus.read_config('FICUS_LOAD_PATH_TEST')
    config_from_string = conficus.read_config(CONTENT)

    assert config_from_path == config_from_string
    assert config_from_env_var == config_from_string


def test_load_with_inheritence():

    config = conficus.load(CONFIG, inheritance=True)

    # sanity check
    assert config['app.debug'] is True

    # validate inheritence took place
    assert 'server' in config['email.errors']

    # validate config is readonly
    assert config.readonly is True


def test_load_with_non_readonly():

    config = conficus.load(CONFIG, inheritance=True, readonly=False)

    # sanity check
    assert config['app.debug'] is True

    # validate no inheritence
    assert 'server' in config['email.errors']

    # validate config is readonly
    assert hasattr(config, 'readonly') is False
