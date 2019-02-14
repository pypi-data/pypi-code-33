import argparse
import logging

# to provide gettext for the overwritten methods from NonExitParser, because the native argparse does so.
try:
    from gettext import gettext as _
except ImportError:
    def _(message):
        return message

# local
try:
    from ts3ekkosingle.errors import EkkoParsingError, EkkoArgparserMessage
except ImportError:
    from .errors import EkkoParsingError, EkkoArgparserMessage

class NonExitParser(argparse.ArgumentParser):
    def exit(self, status=0, message=None):
        if message:
            raise EkkoParsingError(message, self.format_usage())

    def error(self, message):
        args = {'prog': self.prog, 'message': message}
        self.exit(2, _('%(prog)s: error: %(message)s\n') % args)

    def print_help(self, file=None):
        """
        Catch the help generation and raise the flowcontrol EkkoArgparserMessage instead.
        """
        raise EkkoArgparserMessage(self.format_help())

    def print_usage(self, file=None):
        """
        Catch the usage generation and raise the flowcontrol EkkoArgparserMessage instead.
        """
        raise EkkoArgparserMessage(self.format_usage())


class MediaAliasParser:
    @staticmethod
    def parse_queue(cmd_prefix, cmd_str, **kwargs):
        parser = NonExitParser(prog=cmd_prefix, **kwargs)
        parser.add_argument('--position', '-p', type=int)
        parser.add_argument('uri', nargs='+')
        args = parser.parse_args(cmd_str[len(cmd_prefix):].split())
        return args.position, args.uri

    @staticmethod
    def parse_skip(cmd_prefix, cmd_str, **kwargs):
        parser = NonExitParser(prog=cmd_prefix, **kwargs)
        parser.add_argument('count', default=1, nargs='?', type=int)
        args = parser.parse_args(cmd_str[len(cmd_prefix):].split())
        return args.count

    @staticmethod
    def parse_volume(cmd_prefix, cmd_str, **kwargs):
        parser = NonExitParser(prog=cmd_prefix, **kwargs)
        parser.add_argument('percentage', type=int)
        args = parser.parse_args(cmd_str[len(cmd_prefix):].split())
        return args.percentage

    @staticmethod
    def parse_media(cmd_prefix, cmd_str, **kwargs):
        parser = NonExitParser(prog=cmd_prefix, **kwargs)
        parser.add_argument('query_type', nargs='?', type=str)
        args = parser.parse_args(cmd_str[len(cmd_prefix):].split())
        return args.query_type or None

class UtilityParser:
    @staticmethod
    def parse_name(cmd_prefix, cmd_str, **kwargs):
        parser = NonExitParser(prog=cmd_prefix, **kwargs)
        parser.add_argument('name', nargs='+')
        args = parser.parse_args(cmd_str[len(cmd_prefix):].split())
        return ' '.join(args.name)

    @staticmethod
    def parse_noargs(cmd_prefix, cmd_str, **kwargs):
        parser = NonExitParser(prog=cmd_prefix, **kwargs)
        args = parser.parse_args(cmd_str[len(cmd_prefix):].split())
        return args

class FunParser:
    @staticmethod
    def parse_force_dice(cmd_prefix, cmd_str, **kwargs):
        parser = NonExitParser(prog=cmd_prefix, **kwargs)
        parser.add_argument('--force', '-f', action='store_true')
        parser.add_argument('choices', nargs='+')
        args = parser.parse_args(cmd_str[len(cmd_prefix):].split())
        return args.force, args.string
