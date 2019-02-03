import conficus

CONFIG = '''
[app]
debug = True

[email]
server = smtp.email.com
user = smtp-admin
password = smtp-password

[email.errors]
to = admin@email.com

'''


def test_dict_get():

    config = conficus.load(CONFIG)

    # sanity check
    assert config['app.debug'] is True
    assert config['email.errors.to'] == 'admin@email.com'

    assert config.get('email.errors.to', 'foo@email.com') == 'admin@email.com'
    assert config.get('foo.not.there') is None
    assert config.get('foo.not.there', 'no.foo.not.there') == 'no.foo.not.there'
