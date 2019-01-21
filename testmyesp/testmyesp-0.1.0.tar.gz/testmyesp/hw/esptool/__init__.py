
import builtins
import contextlib
import functools
import logging
import tempfile

from colibris import settings
from types import SimpleNamespace

from .esptool import ESP8266ROM
from .esptool import FatalError
from .esptool import write_flash as _write_flash


logging.basicConfig()
logger = logging.getLogger(__name__)


class ESPToolException(Exception):
    pass


class print_to_logger(contextlib.ContextDecorator):
    # override the builtin print() function that is used by esptool.py
    # so we can have the output written to the logger

    def __init__(self):
        self._orig_print = None

    def __enter__(self):
        self._orig_print = builtins.print
        builtins.print = self._log_print

    def __exit__(self, exc_type, exc_value, traceback):
        builtins.print = self._orig_print

    @staticmethod
    def _log_print(msg, *args, **kwargs):
        # ignore short messages that are most likely used to show progress
        if len(msg) < 4:
            return

        if msg.lower().startswith('warning'):
            log_func = logger.warning

        else:
            log_func = logger.debug

        msg = msg.replace('\n', ';')
        msg = msg.replace('\r', ';')
        msg = msg.strip(';')
        log_func(msg)


def replace_exception(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)

        except FatalError as e:
            raise ESPToolException(e)

    return wrapper


def init_esp():
    baud = min(ESP8266ROM.ESP_ROM_BAUD, settings.SERIAL['flash_baud'])

    esp = ESP8266ROM(settings.SERIAL['port'], baud)
    esp.connect()
    esp = esp.run_stub()
    esp.change_baud(settings.SERIAL['flash_baud'])
    esp.flash_set_parameters(settings.FLASH['size'] * 1024)

    return esp


@replace_exception
@print_to_logger()
def write_flash(address, content):
    esp = init_esp()

    with tempfile.NamedTemporaryFile() as tmp_file:
        tmp_file.write(content)
        tmp_file.flush()

        args = SimpleNamespace(compress=None,
                               no_compress=None,
                               no_stub=None,
                               verify=False,
                               flash_size=str(int(settings.FLASH['size'] / 1024)) + 'MB',
                               flash_mode=settings.FLASH['mode'],
                               flash_freq=str(settings.FLASH['freq']) + 'm',
                               addr_filename=[(address, tmp_file)])

        _write_flash(esp, args)

    esp._port.close()  # not cool, but what can we do...


@replace_exception
@print_to_logger()
def read_flash(address, size, progress_func=None):
    esp = init_esp()

    return esp.read_flash(address, size, progress_func)
