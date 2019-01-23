import logging


def get_logger(name, level=logging.INFO, logging_file=None):
    logger = logging.getLogger(name)
    logger.setLevel(level)

    # create a file handler
    if logging_file is None:
        handler = logging.StreamHandler()
    else:
        handler = logging.FileHandler(logging_file)
    handler.setLevel(level)

    # create a logging format
    formatter = logging.Formatter('%(module)s - %(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)

    # add the handlers to the logger
    logger.addHandler(handler)
    return logger