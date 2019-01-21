import logging
import sys


def get_logger(logger_name: str, log_level: int = logging.INFO) -> logging.Logger:
    logger = logging.getLogger(logger_name)
    for h in logger.handlers:
        logger.removeHandler(h)

    h = logging.StreamHandler(sys.stdout)

    log_format = '[%(levelname)s] %(asctime)s - %(name)s: %(message)s'
    h.setFormatter(logging.Formatter(log_format))
    logger.addHandler(h)
    logger.setLevel(log_level)

    return logger
