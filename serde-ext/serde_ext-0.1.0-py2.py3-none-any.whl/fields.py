"""
This module contains extra Field classes for `Models <serde.model.Model>`.
"""

from serde.fields import Str, create

from serde_ext import validate


__all__ = [
    'Domain',
    'Email',
    'IpAddress',
    'Ipv4Address',
    'Ipv6Address',
    'MacAddress',
    'Slug',
    'Url'
]

Domain = create('Domain', base=Str, validators=[validate.domain])
Email = create('Email', base=Str, validators=[validate.email])
IpAddress = create('IpAddress', base=Str, validators=[validate.ip_address])
Ipv4Address = create('Ipv4Address', base=Str, validators=[validate.ipv4_address])
Ipv6Address = create('Ipv6Address', base=Str, validators=[validate.ipv6_address])
MacAddress = create('MacAddress', base=Str, validators=[validate.mac_address])
Slug = create('Slug', base=Str, validators=[validate.slug])
Url = create('Url', base=Str, validators=[validate.url])
