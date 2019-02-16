import logging
import sys

# ==================================================================================================

LOG_FORMAT = (
    "%(asctime)s.%(msecs)03d %(levelname)s %(module)s:%(lineno)s - "
    + "%(funcName)s : %(message)s"
)
DATE_FORMAT = "%Y-%m-%d %H:%M:%S"

# ==================================================================================================


def set_root_logger_stdout(log_level):
    logger = logging.getLogger()
    formatter = logging.Formatter(fmt=LOG_FORMAT, datefmt=DATE_FORMAT)

    handler = logging.StreamHandler(stream=sys.stdout)
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.setLevel(log_level)

    return logger
