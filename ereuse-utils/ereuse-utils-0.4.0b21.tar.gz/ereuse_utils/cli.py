import enum as _enum
import getpass
import pathlib
from typing import Type

from boltons import urlutils
from click import types as click_types

from ereuse_utils import if_none_return_none


class Enum(click_types.Choice):
    """
    Enum support for click.

    Use it as a collection: @click.option(..., type=cli.Enum(MyEnum)).
    Then, this expects you to pass the *name* of a member of the enum.

    From `this github issue <https://github.com/pallets/click/issues/
    605#issuecomment-277539425>`_.
    """

    def __init__(self, enum: Type[_enum.Enum]):
        self.__enum = enum
        super().__init__(enum.__members__)

    def convert(self, value, param, ctx):
        return self.__enum[super().convert(value, param, ctx)]


class Path(click_types.Path):
    """Like click.Path but returning ``pathlib.Path`` objects."""

    def convert(self, value, param, ctx):
        return pathlib.Path(super().convert(value, param, ctx))


class URL(click_types.StringParamType):
    """Returns a bolton's URL.


    """

    name = 'url'

    def __init__(self,
                 scheme=None,
                 username=None,
                 password=None,
                 host=None,
                 port=None,
                 path=None,
                 query_params=None,
                 fragment=None) -> None:
        super().__init__()
        """Creates the type URL. You can require or enforce parts
        of the URL by setting parameters of this constructor.
        
        If the param is...
        
        - None, no check is performed (default).
        - True, it is then required as part of the URL.
        - False, it is then required NOT to be part of the URL.
        - Any other value, then such value is required to be in
          the URL.
        """
        self.attrs = (
            ('scheme', scheme),
            ('username', username),
            ('password', password),
            ('host', host),
            ('port', port),
            ('path', path),
            ('query_params', query_params),
            ('fragment', fragment)
        )

    @if_none_return_none
    def convert(self, value, param, ctx):
        url = urlutils.URL(super().convert(value, param, ctx))
        for name, attr in self.attrs:
            if attr is True:
                if not getattr(url, name):
                    self.fail('URL {} must contain {} but it does not.'.format(url, name))
            elif attr is False:
                if getattr(url, name):
                    self.fail('URL {} cannot contain {} but it does.'.format(url, name))
            elif attr:
                if getattr(url, name) != attr:
                    self.fail('{} form {} can only be {}'.format(name, url, attr))
        return url


def password(service: str, username: str, prompt: str = 'Password:') -> str:
    """Gets a password from the keyring or the terminal."""
    import keyring
    return keyring.get_password(service, username) or getpass.getpass(prompt)
