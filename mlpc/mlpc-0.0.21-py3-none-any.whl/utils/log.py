import os
from functools import reduce
import logging
import mlpc.configuration
import sys


prefix = "MLPC: "
# TODO: MLPC should log, but configuration should have verbosity level


def error(*msg):
    logging.error(_as_single_msg_with_prefix(*msg))


def warning(*msg):
    logging.warning(_as_single_msg_with_prefix(*msg))


def info(*msg):
    logging.info(_as_single_msg_with_prefix(*msg))


def debug(*msg):
    logging.debug(_as_single_msg_with_prefix(*msg))


def _as_single_msg_with_prefix(*msg):
    if len(msg) > 1:
        as_strings = map(lambda x: str(x), msg)
        single_string = reduce(lambda s1, s2: s1 + " " + s2, as_strings)
        return prefix + single_string
    else:
        return prefix + msg[0]


def configure(run):
    if mlpc.configuration.configure_logging:
        log_folder = os.path.join(run.metadata.run_path, "log")
        os.makedirs(log_folder)
        log_file = os.path.join(log_folder, "output.log")

        log_format = "%(asctime)s | %(levelname)s | %(message)s"
        logging.basicConfig(
            format=log_format,
            level=mlpc.configuration.log_level,
            filename=log_file,
            filemode="a"
        )
        console = logging.StreamHandler()
        console.setFormatter(logging.Formatter(log_format))
        logging.getLogger('').addHandler(console)

        if mlpc.configuration.redirect_stdout_to_log:
            StdoutInterceptor().intercept()


class StdoutInterceptor:
    def intercept(self):
        sys.stdout = self

    @staticmethod
    def write(message):
        trimmed_message = message.rstrip()
        if len(trimmed_message) > 0:
            logging.info(trimmed_message)

    def flush(self):
        pass
