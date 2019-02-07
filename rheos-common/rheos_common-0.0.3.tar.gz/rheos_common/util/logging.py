import os
import logging
import time
from logging.handlers import RotatingFileHandler


def setup_root_logger(name_prefix):
    if not os.path.exists("log"):
        os.makedirs("log")

    recfmt = logging.Formatter('%(asctime)s.%(msecs)03d %(levelname)s %(message)s')

    handler = RotatingFileHandler(time.strftime(f"log/{name_prefix}.log"),maxBytes=5000000, backupCount=10)
    handler.setFormatter(recfmt)
    handler.setLevel(logging.DEBUG)

    logger = logging.getLogger()
    logger.addHandler(handler)

    return logger

