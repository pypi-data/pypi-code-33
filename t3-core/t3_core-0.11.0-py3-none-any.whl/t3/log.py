"""Custom logging formatters."""
# pylint: disable=no-self-use
import logging
import json
from contextlib import suppress
from time import gmtime
from time import strftime
from collections import OrderedDict
from pygments import highlight, lexers, formatters


# Use this when doing logs!!!
logger = logging.getLogger('t3')


class StandardFormatter(logging.Formatter):
    """Basic T3 Logging standard implementation."""

    def process(self, record):
        message = record.msg

        # Try to format message w/ args
        if record.args:
            with suppress(TypeError):
                message = message % record.args

        # Try to serialize message into a dict....
        # ...which will then be turned back into json
        with suppress(ValueError, TypeError):
            message = json.loads(message)

        out = OrderedDict([
            ('level', record.levelname),
            ('timestamp', self.format_time(record)),
            ('name', record.name),
            ('message', message),
            # ('path', OrderedDict([
            #     ('module', record.module),
            #     ('file_name', record.filename),
            #     ('line_number', record.lineno),
            #     ('function', record.funcName),
            #     ('path_name', record.pathname),
            # ])),
        ])

        # print(json_traceback())

        if hasattr(record, 'data'):
            out['data'] = record.data

        if record.exc_info or record.stack_info:
            info = record.exc_info if self.formatException(record.exc_info) else None
            stack = record.stack_info if self.formatStack(record.stack_info) else None
            out['exception'] = OrderedDict([
                ('info', info),
                ('stack', stack),
            ])

        return out

    def format(self, record):
        return self.process(record)

    def format_time(self, record, datefmt=None):
        """Format time with microseconds."""
        # pylint: disable=unused-argument
        intl_datetime = strftime('%Y-%m-%d %H:%M:%S', gmtime(record.created))
        return '{}.{}'.format(intl_datetime, int(record.msecs * 1000))


class JsonFormatter(StandardFormatter):
    """Uses python's json module to dump json string of record."""

    def format(self, record):
        try:
            return json.dumps(self.process(record), ensure_ascii=False)
        except Exception as e: # noqa
            return json.dumps({
                "level": 'ERROR',
                "message": 'The logger broke..... (╯°□°)╯︵ ┻━┻',
            }, ensure_ascii=False)


class JsonPrettyFormatter(StandardFormatter):
    """Uses python's pretty format module to pformat record."""

    def format(self, record):
        try:
            return highlight(
                json.dumps(self.process(record), indent=4, ensure_ascii=False),
                lexers.JsonLexer(),
                formatters.TerminalFormatter()
            )
        except Exception as e: # noqa
            return highlight(
                json.dumps({
                    "level": 'ERROR',
                    "message": 'The logger broke..... (╯°□°)╯︵ ┻━┻',
                }, ensure_ascii=False),
                lexers.JsonLexer(),
                formatters.TerminalFormatter()
            )
