"""
Validator functions for use with `Fields <serde.fields.Field>`.
"""

import validators
from serde.exceptions import ValidationError


def domain(value):
    """
    Validate whether or not the given string is a valid domain.

    Args:
        value (str): the value to validate.

    Raises:
        `~serde.exceptions.ValidationError`: when the value is not a valid
            domain.
    """
    if not validators.domain(value):
        raise ValidationError('{!r} is not a valid domain'.format(value))


def email(value):
    """
    Validate whether or not the given string is a valid email.

    Args:
        value (str): the value to validate.

    Raises:
        `~serde.exceptions.ValidationError`: when the value is not a valid
            email.
    """
    if not validators.email(value):
        raise ValidationError('{!r} is not a valid email'.format(value))


def ip_address(value):
    """
    Validate whether or not the given string is a valid IP address.

    Args:
        value (str): the value to validate.

    Raises:
        `~serde.exceptions.ValidationError`: when the value is not a valid IP
            address.
    """
    if not validators.ipv4(value) and not validators.ipv6(value):
        raise ValidationError('{!r} is not a valid IP address'.format(value))


def ipv4_address(value):
    """
    Validate whether or not the given string is a valid IP version 4 address.

    Args:
        value (str): the value to validate.

    Raises:
        `~serde.exceptions.ValidationError`: when the value is not a valid IP
            version 4 address.
    """
    if not validators.ipv4(value):
        raise ValidationError('{!r} is not a valid IPv4 address'.format(value))


def ipv6_address(value):
    """
    Validate whether or not the given string is a valid IP version 6 address.

    Args:
        value (str): the value to validate.

    Raises:
        `~serde.exceptions.ValidationError`: when the value is not a valid IP
            version 6 address.
    """
    if not validators.ipv6(value):
        raise ValidationError('{!r} is not a valid IPv6 address'.format(value))


def mac_address(value):
    """
    Validate whether or not the given string is a valid MAC address.

    Args:
        value (str): the value to validate.

    Raises:
        `~serde.exceptions.ValidationError`: when the value is not a valid MAC
            address.
    """
    if not validators.mac_address(value):
        raise ValidationError('{!r} is not a valid MAC address'.format(value))


def slug(value):
    """
    Validate whether or not the given string is a valid slug.

    Args:
        value (str): the value to validate.

    Raises:
        `~serde.exceptions.ValidationError`: when the value is not a valid slug.
    """
    if not validators.slug(value):
        raise ValidationError('{!r} is not a valid slug'.format(value))


def url(value):
    """
    Validate whether or not the given string is a valid URL.

    Args:
        value (str): the value to validate.

    Raises:
        `~serde.exceptions.ValidationError`: when the value is not a valid URL.
    """
    if not validators.url(value):
        raise ValidationError('{!r} is not a valid URL'.format(value))
