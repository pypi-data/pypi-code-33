import os
import logging
from logging import Formatter, handlers


def setup_logging(path):
    """set up Kev's (me) general purpose, favourite, fantastical logging.
    """
    ROOT_DIR = path
    LOG_DIR = os.path.join(ROOT_DIR, 'logs')
    LOG_FILE = os.path.join(LOG_DIR, 'main.log')
    LOG_FORMAT = '%(asctime)s - %(name)s - %(funcName)s() - %(levelname)s - %(message)s'
    LOG_LVL = logging.DEBUG
    LOG_FILE_SIZE = 50000
    LOG_BACKUP_CNT = 5

    # check if the logs dir exists, otherwise make it
    # if not os.path.isdir(LOG_DIR):
    #     os.mkdir(LOG_DIR)

    # get the root logger, this is SUPER important
    logger = logging.getLogger('')
    # set the level for the root logger
    logger.setLevel(LOG_LVL)
    # create rotating logging handler
    log_handler = logging.handlers.RotatingFileHandler(
        LOG_FILE, maxBytes=LOG_FILE_SIZE, backupCount=LOG_BACKUP_CNT)
    # create the log formatter
    formatter = logging.Formatter(LOG_FORMAT)
    # add formatter to the handler
    log_handler.setFormatter(formatter)
    # add the handler to the logger
    logger.addHandler(log_handler)
    # log a message
    logger.info('starting')

    return logger