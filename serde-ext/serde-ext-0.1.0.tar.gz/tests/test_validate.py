from pytest import raises
from serde.exceptions import ValidationError

from serde_ext import validate


def test_domain():
    validate.domain('www.google.com')

    with raises(ValidationError):
        validate.domain('hello')


def test_email():
    validate.email('someone@website.com')

    with raises(ValidationError):
        validate.email('someone@com')


def test_ip_address():
    validate.ip_address('10.0.0.1')
    validate.ip_address('2001:db8:85a3:0:0:8a2e:370:7334')

    with raises(ValidationError):
        validate.ip_address('10.0.0.256')


def test_ipv4_address():
    validate.ipv4_address('10.0.0.1')

    with raises(ValidationError):
        validate.ipv4_address('10.0.0.256')


def test_ipv6_address():
    validate.ipv6_address('2001:db8:85a3:0:0:8a2e:370:7334')

    with raises(ValidationError):
        validate.ipv6_address('2001:db8:85a3:0:0:8a2e:370:73345')


def test_mac_address():
    validate.mac_address('3a:00:40:82:ad:00')

    with raises(ValidationError):
        validate.mac_address('3a:00:40:82:a:00')


def test_slug():
    validate.slug('a_b-10')

    with raises(ValidationError):
        validate.slug('a!')


def test_url():
    validate.url('http://www.google.com/search?q=test')

    with raises(ValidationError):
        validate.url('derp')
