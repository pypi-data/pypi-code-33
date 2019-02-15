import os
import logging
import time
from logging.handlers import RotatingFileHandler
from logging import StreamHandler


def setup_root_logger(name_prefix, root_log_level=logging.ERROR, logger_type="stream"):
    if not os.path.exists("log"):
        os.makedirs("log")

    recfmt = logging.Formatter('%(asctime)s.%(msecs)03d %(levelname)s %(message)s')

    if logger_type == "file":
        handler = RotatingFileHandler(time.strftime(f"log/{name_prefix}.log"),maxBytes=0, backupCount=0)
    elif logger_type == "stream":
        handler = StreamHandler()
    else:
        print(f"Bad log handler type {logger_type}")
        exit(1)

    handler.setFormatter(recfmt)
    handler.setLevel(root_log_level)

    logger = logging.getLogger()

    logger.setLevel(root_log_level)
    logger.addHandler(handler)

    return logger

