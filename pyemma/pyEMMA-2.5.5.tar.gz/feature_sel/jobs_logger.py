
def get_logger(name, filename):
    import logging, sys
    logger = logging.getLogger('cov_')
    logger.addHandler(logging.FileHandler(filename))
    logger.addHandler(logging.StreamHandler(stream=sys.stdout))
    logger.setLevel('INFO')
    for h in logger.handlers:
        h.add
