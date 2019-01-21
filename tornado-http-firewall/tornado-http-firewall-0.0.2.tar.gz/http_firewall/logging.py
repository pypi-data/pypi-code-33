import logging

parent_logger = logging.getLogger()
console_handler = logging.StreamHandler()
parent_logger.addHandler(console_handler)


def get_logger(name):
    """ Return a child logger """
    return parent_logger.getChild(name)


def set_debug_logging(logger=None):
    """ Set debug level loggin """
    parent_logger.setLevel(logging.DEBUG)
    console_handler.setLevel(logging.DEBUG)
    if logger:
        logger.setLevel(logging.DEBUG)


def logging_shutdown():
    return logging.shutdown()
