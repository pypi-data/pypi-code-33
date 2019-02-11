import logging


class DefaultLogger(object):
    """
    Logger class provides a default logger object. If for any reason the user wants to use a default logger,
    this allows the user to do so without having to import the logging module.
    """
    def __init__(self):
        self.logger = logging.getLogger(__name__)
