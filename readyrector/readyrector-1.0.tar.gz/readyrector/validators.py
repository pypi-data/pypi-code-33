import re
from urllib.parse import urlsplit, urlunsplit

from django.core.exceptions import ValidationError
from django.core.validators import URLValidator, validate_ipv6_address


class PathOrURLValidator(URLValidator):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.regex = re.compile(
            r'^((?:[a-z0-9\.\-\+]*)://'  # scheme is validated separately
            r'(?:\S+(?::\S*)?@)?'  # user:pass authentication
            r'(?:' + self.ipv4_re + '|' + self.ipv6_re + '|' + self.host_re + ')'  # noqa
            r'(?::\d{2,5})?)?'  # port
            r'(?:[/?#][^\s]*)?'  # resource path
            r'\Z', re.IGNORECASE)

    def __call__(self, value):
        # Check first if the scheme is valid
        if not value.startswith('/'):
            scheme = value.split('://')[0].lower()
            if scheme not in self.schemes:
                raise ValidationError(self.message, code=self.code)

        # Then check full URL
        try:
            super(URLValidator, self).__call__(value)
        except ValidationError as e:
            # Trivial case failed. Try for possible IDN domain
            try:
                scheme, netloc, path, query, fragment = urlsplit(value)
            except ValueError:  # for example, "Invalid IPv6 URL"
                raise ValidationError(self.message, code=self.code)
            try:
                netloc = netloc.encode('idna').decode('ascii')
            except UnicodeError:  # invalid domain part
                raise e
            url = urlunsplit((scheme, netloc, path, query, fragment))
            super(URLValidator, self).__call__(url)
        else:
            # Now verify IPv6 in the netloc part
            host_match = re.search(
                r'^\[(.+)\](?::\d{2,5})?$', urlsplit(value).netloc)
            if host_match:
                potential_ip = host_match.groups()[0]
                try:
                    validate_ipv6_address(potential_ip)
                except ValidationError:
                    raise ValidationError(self.message, code=self.code)

        # The maximum length of a full host name is 253 characters per RFC 1034
        # section 3.1. It's defined to be 255 bytes or less, but this includes
        # one byte for the length of the name and one byte for the trailing dot
        # that's used to indicate absolute names in DNS.
        if len(urlsplit(value).netloc) > 253:
            raise ValidationError(self.message, code=self.code)
