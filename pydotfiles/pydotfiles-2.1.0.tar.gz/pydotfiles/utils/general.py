import hashlib
import sys
import logging


"""
General non-project specific helper utilities
"""


class PrettyLogFormatter(logging.Formatter):
    """
    Presentation-layer pretty printing, enabling
    clear guides to an end-user via ANSI escape
    sequences. Should be attached to a logger.

    For more information see:
    https://stackoverflow.com/questions/1343227/can-pythons-logging-format-be-modified-depending-on-the-message-log-level/27835318#27835318
    """

    DEBUG_BLUE = "\033[94m"
    INFO_GREEN = "\033[92m"
    WARNING_YELLOW = "\033[0;33m"
    ERROR_ORANGE = "\033[38:2:255:165:0m"
    FATAL_RED = "\033[31m"

    END_COLOUR = '\033[0m'

    def __init__(self):
        super().__init__()
        self.formatters = {
            logging.DEBUG: logging.Formatter(f"%(asctime)s [{self.DEBUG_BLUE}DEBUG::%(name)s{self.END_COLOUR}]: %(message)s", datefmt=self.date_format),
            logging.INFO: logging.Formatter(f"%(asctime)s [{self.INFO_GREEN}%(levelname)s::%(name)s{self.END_COLOUR}]: %(message)s", datefmt=self.date_format),
            logging.WARNING: logging.Formatter(f"%(asctime)s [{self.WARNING_YELLOW}WARN::%(name)s{self.END_COLOUR}]: %(message)s", datefmt=self.date_format),
            logging.ERROR: logging.Formatter(f"%(asctime)s [{self.ERROR_ORANGE}ERROR::%(name)s{self.END_COLOUR}]: %(message)s", datefmt=self.date_format),
            logging.FATAL: logging.Formatter(f"%(asctime)s [{self.FATAL_RED}FATAL::%(name)s{self.END_COLOUR}]: %(message)s", datefmt=self.date_format),
        }

        self.default_format = logging.Formatter("%(levelname)s: %(name)s: %(message)s")

    @property
    def date_format(self):
        return "%Y-%m-%d %I:%M:%S %p"

    def format(self, record):
        return self.formatters.get(record.levelno, self.default_format).format(record)


class PrettyPrint:
    """
    Presentation-layer pretty printing, enabling
    clear guides to an end-user via ANSI escape
    sequences
    """

    SUCCESS_GREEN = '\033[92m'
    INFO_BLUE = '\033[94m'
    USER_YELLOW = '\033[0;33m'
    WARN_ORANGE = '\033[38:2:255:165:0m'
    FAIL_RED = '\033[31m'

    # Other settings not turned on yet
    # HEADER = '\033[95m'
    # BOLD = '\033[1m'
    # UNDERLINE = '\033[4m'

    END_COLOUR = '\033[0m'

    @staticmethod
    def success(message):
        print(f"[ {PrettyPrint.SUCCESS_GREEN}OK{PrettyPrint.END_COLOUR} ] {message}")

    @staticmethod
    def info(message):
        print(f"[{PrettyPrint.INFO_BLUE}INFO{PrettyPrint.END_COLOUR}] {message}")

    @staticmethod
    def user(message):
        print(f"[{PrettyPrint.USER_YELLOW}USER{PrettyPrint.END_COLOUR}] {message}")

    @staticmethod
    def warn(message):
        print(f"[{PrettyPrint.WARN_ORANGE}WARN{PrettyPrint.END_COLOUR}] {message}")

    @staticmethod
    def fail(message):
        sys.exit(f"[{PrettyPrint.FAIL_RED}FAIL{PrettyPrint.END_COLOUR}] {message}")


class BijectiveDictionary:
    """
    A helpful one-to-one dictionary that has
    some helpful wrappers around a normal dictionary
    with the constraint that the data being input
    is bijective.

    See https://stackoverflow.com/questions/863935/a-data-structure-for-11-mappings-in-python/1374617#1374617
    """

    def __init__(self, input_dictionary=None):
        if input_dictionary is None:
            self.dictionary = {}
        else:
            self.dictionary = input_dictionary.copy()
            for key, value in input_dictionary.items():
                self.dictionary[value] = key

    def add(self, key, value):
        self.dictionary[key] = value
        self.dictionary[value] = key

    def remove(self, key):
        return self.dictionary.pop(self.dictionary.pop(key))

    def get(self, key):
        return self.dictionary.get(key)


"""
General helper functions
"""


def remove_prefix(text, prefix):
    """
    https://stackoverflow.com/questions/16891340/remove-a-prefix-from-a-string/16892491#16892491
    """
    return text[text.startswith(prefix) and len(prefix):]


def hash_file(file_path, block_size=65536):
    """
    Hashes a given file
    """
    hasher = hashlib.sha256()
    with open(file_path, 'rb') as hashed_file:
        buf = hashed_file.read(block_size)
        while len(buf) > 0:
            hasher.update(buf)
            buf = hashed_file.read(block_size)
    return hasher.hexdigest()
